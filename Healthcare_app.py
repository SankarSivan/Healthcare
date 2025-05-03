# Health Dashboard

import mysql.connector
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import json
import requests

# ------------------------ Streamlit Config ----------------------------- #
st.set_page_config(
    page_title="Healthcare Dashboard",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="auto")


# ------------------------- MySQL DB Connection ------------------------- #
conn = mysql.connector.connect(
    host="bkiko7wxgflswme1g31y-mysql.services.clever-cloud.com",
    user="ueezpxgt08vwew78",
    password="Bsq0ZbYQMEayIatAPlkc",
    database="bkiko7wxgflswme1g31y")
cursor = conn.cursor()


# ------------------------ Title ----------------------------- #
# Title in the first row
st.title("Healthcare Dashboard")
st.subheader("Healthcare analysis") 
st.markdown("""
    This dashboard provides insights into healthcare data, including patient demographics, hospital visits, and treatment outcomes.
    Use the sidebar to navigate through different sections and explore the data.""")

# ------------------------ querys ----------------------------- #
cursor.execute("SELECT DISTINCT YEAR(admit_date) from data") #
year_list = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT DISTINCT bed_occupancy from data")
ward_type = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT DISTINCT doctor FROM data")
doctor_list = [row[0] for row in cursor.fetchall()]

#------------------------ Filters ----------------------------- #
col1, col2, col3 = st.columns(3)

with col1:
    year_option = st.selectbox("Select Year", ['All']+ year_list , key='year_list')

with col2:
    ward_option = st.selectbox("Ward Type", ['All'] + ward_type, key='ward_type')

with col3:
    doctor_option = st.selectbox("Doctor", ['All'] + doctor_list, key='doctor_list')


# ----------------------------WHERE Clause ------------------ #
conditions = []
if year_option != 'All':
    conditions.append(f"Year(admit_date)='{year_option}'")
if ward_option != 'All':
    conditions.append(f" bed_occupancy ='{ward_option}'")
if doctor_option != 'All':
    conditions.append(f"doctor='{doctor_option}'")

where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""



# ------------------------- Key KPI Metrics ------------------------- #
st.subheader("📊 Key KPI Metrics")
# First row of metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    cursor.execute(f"SELECT COUNT(patient_ID) FROM data {where_clause}")
    total_patients = cursor.fetchone()[0] or 0
    st.metric("👨‍⚕️ Patients Count", f"{total_patients:,}")

with col2:
    cursor.execute(f"SELECT DATEDIFF(MAX(discharge_date), MIN(admit_date)) FROM data{where_clause}")
    total_days = cursor.fetchone()[0] or 0
    st.metric("📅 Total Days Coverage", f"{total_days:,}")

with col3:
    cursor.execute(f"SELECT COUNT(DISTINCT doctor) FROM data{where_clause}")
    doctor_count = cursor.fetchone()[0] or 0
    st.metric("👩‍⚕️ Total Doctors", f"{doctor_count:,}")

with col4:
    cursor.execute(f"SELECT SUM(Billing_Amount) FROM data{where_clause}")
    total_bill = float(cursor.fetchone()[0] or 0)
    st.metric("💰 Total Bill Amount (₹ Cr)", f"{total_bill/1e7:,.2f}")

# Second row of metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    cursor.execute(f"SELECT COUNT(DISTINCT Diagnosis) FROM data{where_clause}")
    total_Diagnosis = cursor.fetchone()[0] or 0
    st.metric("🩺 Diagnosis Types", f"{total_Diagnosis}")

with col2:
    cursor.execute(f"SELECT COUNT(DISTINCT bed_occupancy) FROM data{where_clause}")
    bed_count = cursor.fetchone()[0] or 0
    st.metric("🏥 Ward Types", f"{bed_count}")

with col3:
    cursor.execute(f"SELECT COUNT(DISTINCT test) FROM data{where_clause}")
    avg_amount = cursor.fetchone()[0] or 0
    st.metric("🧪 Test Types", f"{avg_amount}")
    
with col4:
    cursor.execute(f"SELECT Avg(Billing_Amount) FROM data{where_clause}")
    avg_bill_amount = float(cursor.fetchone()[0] or 0)
    st.metric("💳 Avg Bill Amount (₹)", f"{avg_bill_amount:,.0f}")


# ------------------------- Mothly Trend ------------------------- #
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.subheader("Monthly Trend of Billing Amount & Patient Count")
st.markdown("This chart shows the monthly trend of billing amounts and patient counts.")

# Query data
query = f"""
    SELECT 
        DATE_FORMAT(admit_date, '%Y-%m') AS month_year,
        SUM(Billing_Amount) AS total_billing,
        COUNT(DISTINCT Patient_ID) AS patient_count
    FROM data {where_clause}
    GROUP BY DATE_FORMAT(admit_date, '%Y-%m')
    ORDER BY month_year
"""

cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=["month_year", "total_billing", "patient_count"])

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add billing amount line (primary y-axis)
fig.add_trace(
    go.Scatter(
        x=df["month_year"],
        y=df["total_billing"],
        name="Billing Amount (₹)",
        mode="lines+markers",
        line=dict(color="royalblue", width=2),
        marker=dict(size=12),
        hovertemplate="<b>%{x}</b><br>Billing: ₹%{y:,.2f}<extra></extra>"
    ),
    secondary_y=False,
)

# Add patient count bar (secondary y-axis)
fig.add_trace(
    go.Bar(
        x=df["month_year"],
        y=df["patient_count"],
        name="Patient Count",
        marker_color="rgba(55, 200, 83, 0.6)",
        hovertemplate="<b>%{x}</b><br>Patients: %{y:,}<extra></extra>"
    ),
    secondary_y=True,
)

# Update layout
fig.update_layout(
    #title="Monthly Billing & Patient Visit Trends",
    xaxis=dict(
        title="Month",
        tickangle=45,
        tickvals=df["month_year"][::1]  # Show every month
    ),
    yaxis=dict(
        title="Billing Amount (₹)",
        showgrid=True,
        tickprefix="₹",
        tickformat=",.2f"
    ),
    yaxis2=dict(
        title="Patient Count",
        overlaying="y",
        side="right",
        showgrid=False
    ),
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=50, r=50, b=100, t=50, pad=4)
)

# Show the figure
st.plotly_chart(fig, use_container_width=True)

# Interpretation note
st.caption("💡 Blue line shows billing amounts (left axis), green bars show patient counts (right axis)")



#--------------------------------- Trends of Diagnosis -------------------------------#
# Section Header
st.subheader("Trends of Diagnosis")
st.markdown("This chart shows the trends of diagnosis over the years.")

dia_query = f"""
    SELECT 
        DATE_FORMAT(admit_date, '%Y-%m') AS month_year, 
        Diagnosis, 
        COUNT(*) as count 
    FROM data {where_clause}
    GROUP BY month_year, Diagnosis
    ORDER BY month_year, count DESC
"""

# Fetching data and preparing DataFrame
cursor.execute(dia_query)
df = pd.DataFrame(cursor.fetchall(), columns=["month_year", "Diagnosis", "count"])

# Plotting the line chart
fig = px.line(df, x="month_year", y="count", color="Diagnosis", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Helpful Caption
st.caption("💡 This chart shows the trends of diagnosis and tests over the years.")


#------------------------- Trends of Tests ------------------------- #
# Section Header
st.subheader("Trends of Tests")
st.markdown("This chart shows the trends of tests over the years.")

# Corrected SQL Query
dia_query = f"""
    SELECT 
        DATE_FORMAT(admit_date, '%Y-%m') AS month_year, 
        test, 
        COUNT(*) as count 
    FROM data {where_clause}
    GROUP BY month_year, test
    ORDER BY month_year, count DESC
"""

# Fetching data and preparing DataFrame
cursor.execute(dia_query)
df = pd.DataFrame(cursor.fetchall(), columns=["month_year", "test", "count"])

# Plotting the line chart
fig = px.line(df, x="month_year", y="count", color="test", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Helpful Caption
st.caption("💡 This chart shows the trends of diagnosis and tests over the years.")



# ------------------------- Bed Occupancy ------------------------- #
st.subheader("🛏️ Bed Occupancy Distribution")
st.markdown("This chart shows the distribution of bed occupancy in the hospital.")

bed_query = f"""
    SELECT 
        Bed_Occupancy, 
        COUNT(*) AS count 
    FROM data {where_clause}
    GROUP BY Bed_Occupancy;
"""

cursor.execute(bed_query)
df = pd.DataFrame(cursor.fetchall(), columns=["Bed_Occupancy", "count"])

fig = px.pie(df, names='Bed_Occupancy', values='count',  hole=0.6)
st.plotly_chart(fig, use_container_width=True)

# ------------------------- Length of Stay ------------------------- #
st.subheader("📅 Length of Stay Distribution")

stay_query = f"""
    SELECT 
        Length_of_Stay
    FROM data {where_clause}
    ORDER BY Length_of_Stay DESC;
"""

cursor.execute(stay_query)
df = pd.DataFrame(cursor.fetchall(), columns=["Length_of_Stay"])

fig = px.histogram(df, x='Length_of_Stay', nbins=10,
                   title="📊 Length of Stay Distribution",
                   labels={'Length_of_Stay': 'Number of Days Stayed'})
st.plotly_chart(fig, use_container_width=True)


# ------------------------- Admissions & Discharges Over Time ------------------------- #
st.subheader("📉 Admissions & Discharges Over Time")
st.markdown("This chart shows the trends of admissions and discharges over time.")


# SQL query to fetch admissions and discharges data
Admit_query = f"""
    SELECT 
        Admit_Date AS Date, 
        COUNT(*) AS Admissions,
        0 AS Discharges
    FROM data {where_clause}
    GROUP BY Admit_Date

    UNION ALL

    SELECT 
        Discharge_Date AS Date, 
        0 AS Admissions,
        COUNT(*) AS Discharges
    FROM data {where_clause}
    GROUP BY Discharge_Date
    ORDER BY Date;
    """

cursor.execute(Admit_query)
df = pd.DataFrame(cursor.fetchall(), columns=["Date", "Admissions", "Discharges"])
df['Date'] = pd.to_datetime(df['Date'])
df = df.groupby('Date').sum().reset_index()

fig = px.line(df, x='Date', y=['Admissions', 'Discharges'], markers=True,
              title="📉 Admissions & Discharges Over Time")
st.plotly_chart(fig, use_container_width=True)


# -------------------------- Feedback Score Distribution ------------------------- #
st.subheader("⭐ Feedback Score Distribution")
st.markdown("This chart displays how patients rated their experience on a scale from 1 to 5.")

cursor.execute(f"""
    SELECT 
        Feedback, 
        COUNT(*) AS count
    FROM data {where_clause}
    GROUP BY Feedback
    ORDER BY Feedback;
""")
df = pd.DataFrame(cursor.fetchall(), columns=["Feedback", "count"])

fig = px.bar(df, x='Feedback', y='count', 
             title="Patient Feedback Distribution", 
             labels={'Feedback': 'Feedback Score', 'count': 'Number of Responses'},
             text='count')
st.plotly_chart(fig, use_container_width=True)
st.caption("💡 This chart shows the distribution of feedback scores given by patients.")

#-------------------------- Doctor-wise Average Feedback------------------------- #
st.subheader("👩‍⚕️ Doctor-wise Average Feedback")
st.markdown("This chart compares the average patient feedback received by each doctor.")

cursor.execute(f"""
    SELECT 
        Doctor, 
        ROUND(AVG(Feedback), 2) AS avg_feedback,
        COUNT(*) AS feedback_count
    FROM data {where_clause}
    GROUP BY Doctor
    ORDER BY avg_feedback DESC;
""")
df = pd.DataFrame(cursor.fetchall(), columns=["Doctor", "avg_feedback", "feedback_count"])

fig = px.bar(df, x='Doctor', y='avg_feedback',
             title="Doctor-wise Average Feedback",
             labels={'avg_feedback': 'Average Feedback Score'},
             text='avg_feedback')
st.plotly_chart(fig, use_container_width=True)
st.caption("💡 Doctors with higher average scores indicate better patient satisfaction.")

# ------------------------- Billing Amount by Diagnosis/Test ------------------------- #
st.subheader("💰 Billing Amount by Diagnosis/Test")
st.markdown("This chart highlights which diagnoses and tests contribute most to total billing.")

cursor.execute(f"""
    SELECT 
        Diagnosis,
        Test,
        SUM(Billing_Amount) AS total_billing
    FROM data {where_clause}
    GROUP BY Diagnosis, Test
    ORDER BY total_billing DESC
    LIMIT 10;
""")
df = pd.DataFrame(cursor.fetchall(), columns=["Diagnosis", "Test", "total_billing"])
df["Label"] = df["Diagnosis"] + " - " + df["Test"]

fig = px.treemap(df, 
                 path=['Label'], 
                 values='total_billing',
                 title="Total Billing by Diagnosis and Test")
st.plotly_chart(fig, use_container_width=True)
st.caption("💡 This chart shows the top 10 diagnoses and tests contributing to total billing.")

#------------------------- Billing Range Distribution ------------------------- #
st.subheader("📊 Billing Range Distribution")
st.markdown("This chart shows the spread of billing amounts to detect cost outliers and averages.")

cursor.execute(f"""
    SELECT Billing_Amount
    FROM data {where_clause}
    ORDER BY Billing_Amount DESC;
""")
df = pd.DataFrame(cursor.fetchall(), columns=["Billing_Amount"])

fig = px.histogram(df, x='Billing_Amount', nbins=10,
                   title="Distribution of Billing Amounts",
                   labels={'Billing_Amount': 'Billing Amount (₹)'})
st.plotly_chart(fig, use_container_width=True)
st.caption("💡 This chart shows the distribution of billing amounts.")

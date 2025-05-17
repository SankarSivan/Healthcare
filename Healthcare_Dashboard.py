# ------------------------ Import Libraries ----------------------------- #
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import json
import requests

# ------------------------ Load Data ----------------------------- #
df = pd.read_csv('/workspaces/Healthcare/dataset/Healtcare-Dataset.csv')

# ------------------------ Streamlit Config ----------------------------- #
st.set_page_config(
    page_title="Healthcare Dashboard",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="auto")

# ------------------------ Title ----------------------------- #
# Title in the first row
st.title("Healthcare Dashboard")
st.subheader("Healthcare Analysis") 
st.markdown("""
    This dashboard provides insights into healthcare data, including patient demographics, hospital visits, and treatment outcomes.
    Use the sidebar to navigate through different sections and explore the data.""")


# Ensure date columns are in datetime format
df['admit_date'] = pd.to_datetime(df['admit_date'])

# -------------------- Extract Filter Options -------------------- #
year_list = sorted(df['admit_date'].dt.year.dropna().unique().tolist())
ward_type = sorted(df['bed_occupancy'].dropna().unique().tolist())
doctor_list = sorted(df['doctor'].dropna().unique().tolist())

# -------------------- Streamlit Filter Widgets -------------------- #
col1, col2, col3 = st.columns(3)

with col1:
    year_option = st.selectbox("Select Year", ['All'] + year_list, key='year_list')

with col2:
    ward_option = st.selectbox("Ward Type", ['All'] + ward_type, key='ward_type')

with col3:
    doctor_option = st.selectbox("Doctor", ['All'] + doctor_list, key='doctor_list')

# -------------------- Apply Filtering Using Pandas -------------------- #
filtered_df = df.copy()

if year_option != 'All':
    filtered_df = filtered_df[filtered_df['admit_date'].dt.year == year_option]

if ward_option != 'All':
    filtered_df = filtered_df[filtered_df['bed_occupancy'] == ward_option]

if doctor_option != 'All':
    filtered_df = filtered_df[filtered_df['doctor'] == doctor_option]

# -------------------- Display or Use Filtered Data -------------------- #
st.write("Filtered Records:", filtered_df.shape[0])
st.dataframe(filtered_df.head())

# ------------------------- Key KPI Metrics (using aggr_trans) ------------------------- #
#  First row of metrics (Transaction metrics)
st.subheader("📊 Key KPI Metrics")

filtered_df['admit_date'] = pd.to_datetime(filtered_df['admit_date'], errors='coerce')
filtered_df['discharge_date'] = pd.to_datetime(filtered_df['discharge_date'], errors='coerce')

# -------------------- First Row of KPIs -------------------- #
col1,col2, col3, col4 = st.columns(4)

with col1:
    total_patients = filtered_df['patient_id'].nunique()
    st.metric("Patients Count", f"{total_patients:,}")

with col2:
    total_days = filtered_df['admit_date'].nunique()

    if not filtered_df.empty:
        total_days = (filtered_df['discharge_date'].max() - filtered_df['admit_date'].min()).days
    else:
        total_days = 0
    st.metric("📅 Total Days Coverage", f"{total_days:,}")

with col3:
    doctor_count = filtered_df['doctor'].nunique()
    st.metric("👩‍⚕️ Total Doctors", f"{doctor_count:,}")

with col4:
    total_bill = filtered_df['billing_amount'].sum()
    st.metric("💰 Total Bill Amount (₹ Cr)", f"{total_bill / 1e7:,.2f}")

# -------------------- Second Row of KPIs -------------------- #
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_diagnosis = filtered_df['diagnosis'].nunique()
    st.metric("🩺 Diagnosis Types", f"{total_diagnosis}")

with col2:
    bed_count = filtered_df['bed_occupancy'].nunique()
    st.metric("🏥 Ward Types", f"{bed_count}")

with col3:
    test_count = filtered_df['test'].nunique()
    st.metric("🧪 Test Types", f"{test_count}")

with col4:
    avg_bill_amount = filtered_df['billing_amount'].mean()
    st.metric("💳 Avg Bill Amount (₹)", f"{avg_bill_amount:,.0f}")



# ------------------------- Mothly Trend ------------------------- #

st.subheader("Monthly Trend of Billing Amount & Patient Count")
st.markdown("This chart shows the monthly trend of billing amounts and patient counts.")

# Ensure datetime format
filtered_df['admit_date'] = pd.to_datetime(filtered_df['admit_date'], errors='coerce')

# Create month-year column
filtered_df['month_year'] = filtered_df['admit_date'].dt.to_period('M').astype(str)

# Aggregate monthly data
monthly_data = filtered_df.groupby('month_year').agg({
    'billing_amount': 'sum',
    'patient_id': pd.Series.nunique
}).reset_index().rename(columns={
    'billing_amount': 'total_billing',
    'patient_id': 'patient_count'
})

# Sort for proper line plot
monthly_data = monthly_data.sort_values('month_year')

# Plot
fig, ax1 = plt.subplots(figsize=(12, 6))

# Line for billing
sns.lineplot(data=monthly_data, x='month_year', y='total_billing', marker='o', color='blue', label='Billing Amount (₹)', ax=ax1)
ax1.set_ylabel("Billing Amount (₹)", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_xticklabels(monthly_data['month_year'], rotation=45)

# Twin axis for patient count
ax2 = ax1.twinx()
sns.barplot(data=monthly_data, x='month_year', y='patient_count', alpha=0.5, color='green', label='Patient Count', ax=ax2)
ax2.set_ylabel("Patient Count", color='green')
ax2.tick_params(axis='y', labelcolor='green')

# Title and layout
fig.tight_layout()
st.pyplot(fig)

st.caption("💡 Blue line shows billing amounts (left axis), green bars show patient counts (right axis).")


# ------------------------- Trends of Diagnosis ------------------------- #
st.subheader("Trends of Diagnosis")
st.markdown("This chart shows the trends of diagnosis over the years.")

# Make sure 'admit_date' is in datetime format
filtered_df['admit_date'] = pd.to_datetime(filtered_df['admit_date'], errors='coerce')
filtered_df['month_year'] = filtered_df['admit_date'].dt.to_period('M').astype(str)

# Count patients by month and diagnosis
diagnosis_counts = filtered_df.groupby(['month_year', 'diagnosis']).size().reset_index(name='patient_count')
diagnosis_counts = diagnosis_counts.sort_values("month_year")

# Plot
plt.figure(figsize=(14, 7))
sns.lineplot(data=diagnosis_counts, x='month_year', y='patient_count', hue='diagnosis', marker='o')

# Styling
plt.title("Diagnosis Trends Over Time")
plt.xlabel("Month-Year")
plt.ylabel("Patient Count")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

# Show on Streamlit
st.pyplot(plt)

st.caption("💡 This chart shows the trends of diagnosis over the years.")









#-----------------Trends of Tests------------#

import seaborn as sns
import matplotlib.pyplot as plt

st.subheader("Trends of Tests")
st.markdown("This chart shows the trends of tests over the years.")

# Ensure datetime and month_year
filtered_df['admit_date'] = pd.to_datetime(filtered_df['admit_date'], errors='coerce')
filtered_df['month_year'] = filtered_df['admit_date'].dt.to_period('M').astype(str)

# Group and count
test_count = filtered_df.groupby(['month_year', 'test']).size().reset_index(name='patient_count')
test_count = test_count.sort_values("month_year")

# Plot
plt.figure(figsize=(14, 7))
sns.lineplot(data=test_count, x='month_year', y='patient_count', hue='test', marker='o')

# Styling
plt.title("Test Trends Over Time")
plt.xlabel("Month-Year")
plt.ylabel("Patient Count")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

# Show in Streamlit
st.pyplot(plt)

st.caption("💡 This chart shows the trends of tests over the years.")


#--------------------Bed Occupancy Distribution----------------------#

import seaborn as sns
import matplotlib.pyplot as plt

st.subheader("🛏️ Bed Occupancy Distribution")
st.markdown("This histogram shows the frequency of each bed occupancy type.")

# Plot histogram (bar plot for categorical data)
plt.figure(figsize=(8, 5))
sns.countplot(data=filtered_df, x='bed_occupancy', palette='pastel')

plt.xlabel("Bed Occupancy Type")
plt.ylabel("Number of Patients")
plt.title("Bed Occupancy Distribution")
plt.xticks(rotation=45)
plt.tight_layout()

# Show in Streamlit
st.pyplot(plt)


# -----------------Length of Stay Distribution --------------------------------#

# Ensure date columns are in datetime format
filtered_df['admit_date'] = pd.to_datetime(filtered_df['admit_date'], errors='coerce')
filtered_df['discharge_date'] = pd.to_datetime(filtered_df['discharge_date'], errors='coerce')

# Calculate Length of Stay
filtered_df['Length_of_Stay'] = (filtered_df['discharge_date'] - filtered_df['admit_date']).dt.days

# Remove invalid or negative stays (optional but recommended)
filtered_df = filtered_df[filtered_df['Length_of_Stay'] >= 0]

# Plot Length of Stay Distribution
st.subheader("📅 Length of Stay Distribution")
st.markdown("This histogram shows how long patients typically stay in the hospital.")

plt.figure(figsize=(8, 5))
sns.histplot(filtered_df['Length_of_Stay'], bins=10, kde=True, color="skyblue")

plt.xlabel("Number of Days Stayed")
plt.ylabel("Number of Patients")
plt.title("📊 Length of Stay Distribution")
plt.tight_layout()

st.pyplot(plt)




import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.subheader("📉 Admissions & Discharges Over Time")
st.markdown("This chart shows the trends of admissions and discharges over time.")

# Make sure date columns are datetime
filtered_df['admit_date'] = pd.to_datetime(filtered_df['admit_date'], errors='coerce')
filtered_df['discharge_date'] = pd.to_datetime(filtered_df['discharge_date'], errors='coerce')

# Create admissions DataFrame
admit_df = filtered_df[['admit_date']].copy()
admit_df = admit_df.dropna()
admit_df['Date'] = admit_df['admit_date'].dt.date
admit_df['Admissions'] = 1

# Create discharges DataFrame
discharge_df = filtered_df[['discharge_date']].copy()
discharge_df = discharge_df.dropna()
discharge_df['Date'] = discharge_df['discharge_date'].dt.date
discharge_df['Discharges'] = 1

# Group by Date
admit_grouped = admit_df.groupby('Date')['Admissions'].sum().reset_index()
discharge_grouped = discharge_df.groupby('Date')['Discharges'].sum().reset_index()

# Merge both DataFrames
df = pd.merge(admit_grouped, discharge_grouped, on='Date', how='outer').fillna(0)
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')

# Melt for Seaborn
df_melted = df.melt(id_vars='Date', value_vars=['Admissions', 'Discharges'],
                    var_name='Event', value_name='Count')

# Plot
plt.figure(figsize=(12, 6))
sns.lineplot(data=df_melted, x='Date', y='Count', hue='Event', marker='o')
plt.title("📉 Admissions & Discharges Over Time")
plt.xlabel("Date")
plt.ylabel("Number of Patients")
plt.xticks(rotation=45)
plt.tight_layout()

# Display in Streamlit
st.pyplot(plt)


#---------------------------Feedback Score Distribution------------------#
st.subheader("⭐ Feedback Score Distribution")
st.markdown("This chart displays how patients rated their experience on a scale from 1 to 5.")

# Ensure column name is lowercase
filtered_df.columns = [col.lower() for col in filtered_df.columns]

# Drop NA feedbacks and convert to integer (if needed)
feedback_df = filtered_df[['feedback']].dropna()
feedback_df['feedback'] = feedback_df['feedback'].astype(int)

# Plot
plt.figure(figsize=(8, 5))
sns.countplot(data=feedback_df, x='feedback', palette='Blues', edgecolor='black')

plt.title("Patient Feedback Distribution")
plt.xlabel("Feedback Score")
plt.ylabel("Number of Responses")

# Annotate bars with counts
for p in plt.gca().patches:
    height = p.get_height()
    plt.gca().annotate(f'{int(height)}', 
                       (p.get_x() + p.get_width() / 2., height), 
                       ha='center', va='bottom')

plt.tight_layout()
st.pyplot(plt)

# Caption
st.caption("💡 This chart shows the distribution of feedback scores given by patients.")

import seaborn as sns
import matplotlib.pyplot as plt

st.subheader("👩‍⚕️ Doctor-wise Average Feedback")
st.markdown("This chart compares the average patient feedback received by each doctor.")

# Ensure consistent lowercase column names
filtered_df.columns = [col.lower() for col in filtered_df.columns]

# Drop nulls and ensure proper dtypes
feedback_df = filtered_df[['doctor', 'feedback']].dropna()
feedback_df['feedback'] = feedback_df['feedback'].astype(float)

# Group by doctor and calculate average feedback
doctor_feedback = feedback_df.groupby('doctor')['feedback'].agg(['mean', 'count']).reset_index()
doctor_feedback = doctor_feedback.sort_values(by='mean', ascending=False)

# Plot
plt.figure(figsize=(10, 6))
sns.barplot(data=doctor_feedback, x='doctor', y='mean', palette='viridis', edgecolor='black')

plt.title("Doctor-wise Average Feedback")
plt.xlabel("Doctor")
plt.ylabel("Average Feedback Score")

# Annotate bars
for p in plt.gca().patches:
    height = p.get_height()
    plt.gca().annotate(f'{height:.2f}', 
                       (p.get_x() + p.get_width() / 2., height), 
                       ha='center', va='bottom')

plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(plt)

st.caption("💡 Doctors with higher average scores indicate better patient satisfaction.")


st.subheader("💰 Billing Amount by Diagnosis/Test")
st.markdown("This chart highlights which diagnoses and tests contribute most to total billing.")

# Drop nulls and clean data
billing_df = filtered_df[['diagnosis', 'test', 'billing_amount']].dropna()
billing_df['billing_amount'] = billing_df['billing_amount'].astype(float)

# Group and aggregate
billing_summary = billing_df.groupby(['diagnosis', 'test'])['billing_amount'].sum().reset_index()
billing_summary['label'] = billing_summary['diagnosis'] + " - " + billing_summary['test']
billing_summary = billing_summary.sort_values(by='billing_amount', ascending=False).head(10)

# Plot
plt.figure(figsize=(10, 6))
sns.barplot(data=billing_summary, y='label', x='billing_amount', palette='magma')

plt.title("Top 10 Billing by Diagnosis and Test")
plt.xlabel("Total Billing Amount")
plt.ylabel("Diagnosis - Test")

# Annotate bars
for p in plt.gca().patches:
    width = p.get_width()
    plt.gca().annotate(f'{width:.0f}', 
                       (width, p.get_y() + p.get_height() / 2), 
                       ha='left', va='center')

plt.tight_layout()
st.pyplot(plt)

st.caption("💡 This chart shows the top 10 diagnoses and tests contributing to total billing.")



#---------------Billing Range Distribution-------------------#
st.subheader("📊 Billing Range Distribution")
st.markdown("This chart shows the spread of billing amounts to detect cost outliers and averages.")

# Drop missing values and convert to numeric if necessary
billing_df = filtered_df[['billing_amount']].dropna()
billing_df['billing_amount'] = billing_df['billing_amount'].astype(float)

plt.figure(figsize=(10, 6))
sns.histplot(billing_df['billing_amount'], bins=10, kde=False, color='skyblue')

plt.title("Distribution of Billing Amounts")
plt.xlabel("Billing Amount (₹)")
plt.ylabel("Count")
plt.tight_layout()

st.pyplot(plt)

st.caption("💡 This chart shows the distribution of billing amounts.")

# ----------------- Frequency of Tests Conducted -------------------#
st.subheader("🧪 Frequency of Tests Conducted-33")
st.markdown("This chart shows how often each test type was conducted in the dataset.")

test_counts = filtered_df['test'].value_counts().reset_index()
test_counts.columns = ['Test Type', 'Number of Tests']

# Show the table of counts in Streamlit
#st.dataframe(test_counts)

fig = px.bar(
    test_counts,
    x='Test Type',
    y='Number of Tests',
    title='Frequency of Tests Conducted',
    labels={'Test Type': 'Test Type', 'Number of Tests': 'Number of Tests'},
    color='Test Type',
    text='Number of Tests'  # Show value on each bar
)
fig.update_traces(textposition='outside')
st.plotly_chart(fig, use_container_width=True)


# ----------------- Diagnosis Distribution Pie Chart -------------------#
st.subheader("🩺 Diagnosis Distribution")
st.markdown("This chart shows the distribution of diagnoses in the dataset.")

diagnosis_counts = filtered_df['diagnosis'].value_counts().reset_index()
diagnosis_counts.columns = ['Diagnosis', 'Count']

fig = px.pie(
    diagnosis_counts,
    values='Count',
    names='Diagnosis',
    title='Distribution of Diagnoses',
    hole=0.4  # Creates a donut chart
)
fig.update_traces(textinfo='percent+label+value')
st.plotly_chart(fig, use_container_width=True)


# ----------------- Doctor-wise Treatment/Test Patterns -------------------#
st.subheader("👨‍⚕️ Doctor-wise Treatment/Test Patterns")
st.markdown("This chart shows how many times each doctor conducted each test.")

doctor_test_counts = filtered_df.groupby(['doctor', 'test']).size().reset_index(name='Count')

fig = px.bar(
    doctor_test_counts,
    x='doctor',
    y='Count',
    color='test',
    title='Doctor-wise Test Patterns',
    labels={'Count': 'Number of Tests', 'doctor': 'Doctor', 'test': 'Test'},
    barmode='stack',  # Use 'group' for grouped bar chart
    text='Count'      # Show count on each bar
)
fig.update_traces(textposition='outside')
st.plotly_chart(fig, use_container_width=True)

import plotly.express as px

# Count admissions per day
admit_trend = df['admit_date'].value_counts().reset_index()
admit_trend.columns = ['Date', 'Admissions']
admit_trend = admit_trend.sort_values('Date')

# Count discharges per day
discharge_trend = df['discharge_date'].value_counts().reset_index()
discharge_trend.columns = ['Date', 'Discharges']
discharge_trend = discharge_trend.sort_values('Date')

# Merge trends
trend_df = pd.merge(admit_trend, discharge_trend, on='Date', how='outer').fillna(0)
trend_df = trend_df.sort_values('Date')

# Plot with Plotly in Streamlit
fig = px.line(
    trend_df,
    x='Date',
    y=['Admissions', 'Discharges'],
    title='Admission and Discharge Trends Over Time',
    labels={'value': 'Count', 'variable': 'Event'}
)
st.plotly_chart(fig, use_container_width=True)
# ------------------------ Import Libraries ----------------------------- #
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ------------------------ Load Data ----------------------------- #
df = pd.read_csv('/workspaces/Healthcare/dataset/Healtcare-Dataset.csv')

# Convert date columns to datetime
df['admit_date'] = pd.to_datetime(df['admit_date'])
df['discharge_date'] = pd.to_datetime(df['discharge_date'])

# ------------------------ Streamlit Config ----------------------------- #
st.set_page_config(
    page_title="Healthcare Dashboard",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="auto")

# ------------------------ Title ----------------------------- #
st.title("🏥 Healthcare Dashboard")
st.markdown("""
    This dashboard provides insights into hospital patient data including:
    - Patient demographics
    - Treatment patterns
    - Financial metrics
    - Performance indicators
""")

# -------------------- Sidebar Filters -------------------- #
st.sidebar.header("Filters")

# Get unique values for filters
years = sorted(df['admit_date'].dt.year.unique())
wards = sorted(df['bed_occupancy'].unique())
doctors = sorted(df['doctor'].unique())

# Create filters in sidebar
selected_year = st.sidebar.selectbox("Select Year", ['All'] + years)
selected_ward = st.sidebar.selectbox("Select Ward Type", ['All'] + wards)
selected_doctor = st.sidebar.selectbox("Select Doctor", ['All'] + doctors)

# Apply filters
filtered_df = df.copy()
if selected_year != 'All':
    filtered_df = filtered_df[filtered_df['admit_date'].dt.year == selected_year]
if selected_ward != 'All':
    filtered_df = filtered_df[filtered_df['bed_occupancy'] == selected_ward]
if selected_doctor != 'All':
    filtered_df = filtered_df[filtered_df['doctor'] == selected_doctor]

# -------------------- Key Metrics -------------------- #
st.header("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Patients", filtered_df['patient_id'].nunique())
with col2:
    st.metric("Total Doctors", filtered_df['doctor'].nunique())
with col3:
    st.metric("Total Billing", f"₹{filtered_df['billing_amount'].sum():,.0f}")
with col4:
    st.metric("Avg Stay Days", round((filtered_df['discharge_date'] - filtered_df['admit_date']).dt.days.mean(), 1))

# -------------------- Charts Section -------------------- #
st.header("📈 Data Visualizations")

# 1. Monthly Trends
st.subheader("Monthly Patient & Billing Trends")
monthly_data = filtered_df.groupby(filtered_df['admit_date'].dt.to_period('M')).agg({
    'patient_id': 'count',
    'billing_amount': 'sum'
}).reset_index()
monthly_data['admit_date'] = monthly_data['admit_date'].astype(str)

fig, ax1 = plt.subplots(figsize=(10,5))
ax1.plot(monthly_data['admit_date'], monthly_data['patient_id'], color='blue', marker='o')
ax1.set_ylabel('Patient Count', color='blue')
ax2 = ax1.twinx()
ax2.bar(monthly_data['admit_date'], monthly_data['billing_amount'], alpha=0.3, color='green')
ax2.set_ylabel('Billing Amount', color='green')
plt.xticks(rotation=45)
st.pyplot(fig)

# 2. Diagnosis Distribution
st.subheader("Patient Diagnosis Distribution")
diagnosis_counts = filtered_df['diagnosis'].value_counts().reset_index()
diagnosis_counts.columns = ['Diagnosis', 'Count']

fig = px.pie(diagnosis_counts, values='Count', names='Diagnosis', 
             title='Diagnosis Distribution', hole=0.4)
st.plotly_chart(fig)

# 3. Test Frequency
st.subheader("Medical Tests Frequency")
test_counts = filtered_df['test'].value_counts().reset_index()
test_counts.columns = ['Test', 'Count']

fig = px.bar(test_counts, x='Test', y='Count', color='Test',
             title='Number of Tests Conducted')
st.plotly_chart(fig)

# 4. Doctor Performance
st.subheader("Doctor Performance Metrics")
doctor_stats = filtered_df.groupby('doctor').agg({
    'patient_id': 'count',
    'billing_amount': 'mean',
    'feedback': 'mean'
}).reset_index()

fig = px.bar(doctor_stats, x='doctor', y='patient_id', 
             title='Patients Treated by Each Doctor')
st.plotly_chart(fig)

fig = px.bar(doctor_stats, x='doctor', y='feedback', 
             title='Average Feedback by Doctor')
st.plotly_chart(fig)

# 5. Ward Occupancy
st.subheader("Ward/Bed Occupancy")
ward_counts = filtered_df['bed_occupancy'].value_counts().reset_index()
ward_counts.columns = ['Ward', 'Count']

fig = px.bar(ward_counts, x='Ward', y='Count', color='Ward',
             title='Bed Occupancy by Ward Type')
st.plotly_chart(fig)

# -------------------- Raw Data Preview -------------------- #
st.header("🔍 Data Preview")
st.dataframe(filtered_df.head())

# -------------------- Footer -------------------- #
st.markdown("---")
st.markdown("Healthcare Dashboard v1.0 | Created with Streamlit")
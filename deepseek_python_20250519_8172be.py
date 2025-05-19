# ------------------------ Import Libraries ----------------------------- #
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ------------------------ Load Data ----------------------------- #
#@st.cache_data
def load_data():
    return pd.read_csv('D:\VSCode\Presonal_Project\Healthcare\Healtcare-Dataset.xlsx')

df = load_data()

# ------------------------ Streamlit Config ----------------------------- #
st.set_page_config(
    page_title="Healthcare Dashboard",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="auto")

# ------------------------ Helper Functions ----------------------------- #
def setup_filters(df):
    """Prepare filter options from the dataframe"""
    df['admit_date'] = pd.to_datetime(df['admit_date'])
    year_list = sorted(df['admit_date'].dt.year.dropna().unique().tolist())
    ward_type = sorted(df['bed_occupancy'].dropna().unique().tolist())
    doctor_list = sorted(df['doctor'].dropna().unique().tolist())
    return year_list, ward_type, doctor_list

def apply_filters(df, year, ward, doctor):
    """Apply filters to the dataframe"""
    filtered_df = df.copy()
    
    if year != 'All':
        filtered_df = filtered_df[filtered_df['admit_date'].dt.year == year]
    if ward != 'All':
        filtered_df = filtered_df[filtered_df['bed_occupancy'] == ward]
    if doctor != 'All':
        filtered_df = filtered_df[filtered_df['doctor'] == doctor]
    
    return filtered_df

def display_kpis(filtered_df):
    """Display key performance indicators"""
    # First row of KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Patients Count", f"{filtered_df['patient_id'].nunique():,}")
    with col2:
        total_days = (filtered_df['discharge_date'].max() - filtered_df['admit_date'].min()).days if not filtered_df.empty else 0
        st.metric("Total Days Coverage", f"{total_days:,}")
    with col3:
        st.metric("Total Doctors", f"{filtered_df['doctor'].nunique():,}")
    with col4:
        st.metric("Total Bill Amount (₹ Cr)", f"{filtered_df['billing_amount'].sum() / 1e7:,.2f}")

    # Second row of KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Diagnosis Types", f"{filtered_df['diagnosis'].nunique()}")
    with col2:
        st.metric("Ward Types", f"{filtered_df['bed_occupancy'].nunique()}")
    with col3:
        st.metric("Test Types", f"{filtered_df['test'].nunique()}")
    with col4:
        st.metric("Avg Bill Amount (₹)", f"{filtered_df['billing_amount'].mean():,.0f}")

def plot_monthly_trend(filtered_df):
    """Plot monthly trend of billing and patient count"""
    filtered_df['month_year'] = filtered_df['admit_date'].dt.to_period('M').astype(str)
    monthly_data = filtered_df.groupby('month_year').agg({
        'billing_amount': 'sum',
        'patient_id': pd.Series.nunique
    }).reset_index().rename(columns={
        'billing_amount': 'total_billing',
        'patient_id': 'patient_count'
    }).sort_values('month_year')

    fig, ax1 = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly_data, x='month_year', y='total_billing', 
                 marker='o', color='blue', label='Billing Amount (₹)', ax=ax1)
    ax1.set_ylabel("Billing Amount (₹)", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.set_xticklabels(monthly_data['month_year'], rotation=45)

    ax2 = ax1.twinx()
    sns.barplot(data=monthly_data, x='month_year', y='patient_count', 
                alpha=0.5, color='green', label='Patient Count', ax=ax2)
    ax2.set_ylabel("Patient Count", color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    fig.tight_layout()
    st.pyplot(fig)
    st.caption("💡 Blue line shows billing amounts (left axis), green bars show patient counts (right axis).")

def plot_diagnosis_trends(filtered_df):
    """Plot diagnosis trends over time"""
    filtered_df['month_year'] = filtered_df['admit_date'].dt.to_period('M').astype(str)
    diagnosis_counts = filtered_df.groupby(['month_year', 'diagnosis']).size().reset_index(name='patient_count')
    diagnosis_counts = diagnosis_counts.sort_values("month_year")

    plt.figure(figsize=(14, 7))
    sns.lineplot(data=diagnosis_counts, x='month_year', y='patient_count', hue='diagnosis', marker='o')
    plt.title("Diagnosis Trends Over Time")
    plt.xlabel("Month-Year")
    plt.ylabel("Patient Count")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)
    st.caption("💡 This chart shows the trends of diagnosis over the years.")

def plot_bed_occupancy(filtered_df):
    """Plot bed occupancy distribution"""
    plt.figure(figsize=(8, 5))
    sns.countplot(data=filtered_df, x='bed_occupancy', palette='pastel')
    plt.xlabel("Bed Occupancy Type")
    plt.ylabel("Number of Patients")
    plt.title("Bed Occupancy Distribution")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

def plot_feedback_distribution(filtered_df):
    """Plot patient feedback distribution"""
    feedback_df = filtered_df[['feedback']].dropna()
    feedback_df['feedback'] = feedback_df['feedback'].astype(int)

    plt.figure(figsize=(8, 5))
    ax = sns.countplot(data=feedback_df, x='feedback', palette='Blues', edgecolor='black')
    plt.title("Patient Feedback Distribution")
    plt.xlabel("Feedback Score")
    plt.ylabel("Number of Responses")

    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f'{int(height)}', 
                   (p.get_x() + p.get_width() / 2., height), 
                   ha='center', va='bottom')

    plt.tight_layout()
    st.pyplot(plt)
    st.caption("💡 This chart shows the distribution of feedback scores given by patients.")

# ------------------------ Main Dashboard ----------------------------- #
def main():
    # Title and description
    st.title("Healthcare Dashboard")
    st.subheader("Healthcare Analysis") 
    st.markdown("""
        This dashboard provides insights into healthcare data, including patient demographics, 
        hospital visits, and treatment outcomes. Use the filters to explore the data.""")

    # Setup and display filters
    year_list, ward_type, doctor_list = setup_filters(df)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        year_option = st.selectbox("Select Year", ['All'] + year_list)
    with col2:
        ward_option = st.selectbox("Ward Type", ['All'] + ward_type)
    with col3:
        doctor_option = st.selectbox("Doctor", ['All'] + doctor_list)

    # Apply filters
    filtered_df = apply_filters(df, year_option, ward_option, doctor_option)
    
    # Display filtered data summary
    st.write(f"Filtered Records: {filtered_df.shape[0]}")
    if st.checkbox("Show filtered data"):
        st.dataframe(filtered_df.head())

    # Display KPIs
    st.subheader("📊 Key KPI Metrics")
    display_kpis(filtered_df)

    # Visualizations
    st.subheader("📈 Data Visualizations")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Monthly Trends", "Diagnosis Analysis", "Bed Occupancy", 
        "Patient Feedback", "Other Metrics"
    ])
    
    with tab1:
        st.subheader("Monthly Trend of Billing Amount & Patient Count")
        plot_monthly_trend(filtered_df)
        
    with tab2:
        st.subheader("Diagnosis Trends")
        plot_diagnosis_trends(filtered_df)
        
    with tab3:
        st.subheader("🛏️ Bed Occupancy Distribution")
        plot_bed_occupancy(filtered_df)
        
    with tab4:
        st.subheader("⭐ Feedback Score Distribution")
        plot_feedback_distribution(filtered_df)
        
    with tab5:
        st.subheader("Additional Metrics")
        # Add other visualizations here as needed

if __name__ == "__main__":
    main()
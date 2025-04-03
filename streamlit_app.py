import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Page config
st.set_page_config(page_title="Hospital Performance Dashboard", layout="wide")
st.title("\U0001F3E5 Hospital Performance Dashboard")
st.markdown("Explore patient data, conditions, and hospital performance metrics interactively.")

# Load CSV
@st.cache_data
def load_data():
    df = pd.read_csv("data/patient_data_cleaned.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("\U0001F50D Filter Patients")
gender = st.sidebar.selectbox("Select Gender", ["All"] + sorted(df["gender"].dropna().unique().tolist()))
condition = st.sidebar.selectbox("Select Medical Condition", ["All"] + sorted(df["medical_condition"].dropna().unique().tolist()))
doctor = st.sidebar.selectbox("Select Doctor", ["All"] + sorted(df["doctor"].dropna().unique().tolist()))

# Date range filter
min_date = pd.to_datetime(df["date_of_admission"]).min()
max_date = pd.to_datetime(df["date_of_admission"]).max()
start_date, end_date = st.sidebar.date_input("Select Admission Date Range", [min_date, max_date])

# Filtering
filtered_df = df.copy()
if gender != "All":
    filtered_df = filtered_df[filtered_df["gender"].str.lower() == gender.lower()]
if condition != "All":
    filtered_df = filtered_df[filtered_df["medical_condition"].str.lower() == condition.lower()]
if doctor != "All":
    filtered_df = filtered_df[filtered_df["doctor"].str.lower() == doctor.lower()]

filtered_df = filtered_df[
    (pd.to_datetime(filtered_df["date_of_admission"]) >= pd.to_datetime(start_date)) &
    (pd.to_datetime(filtered_df["date_of_admission"]) <= pd.to_datetime(end_date))
]

# KPI Metrics
st.markdown("### \U0001F4CA Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Patients", len(filtered_df))
col2.metric("Avg Length of Stay", round(filtered_df["length_of_stay"].mean(), 2))
col3.metric("Unique Conditions", filtered_df["medical_condition"].nunique())
if "billing_amount" in filtered_df.columns:
    col4.metric("Avg Billing Amount", f"${filtered_df['billing_amount'].mean():,.2f}")
#st.subheader("🏥 Hospital Ratings Overview")

# Add download button
st.markdown("### ⬇️ Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download as CSV",
    data=csv,
    file_name='filtered_patient_data.csv',
    mime='text/csv'
)

# Top Conditions Plot
st.markdown("### \U0001F4CA Top 10 Medical Conditions")
top_conditions = filtered_df["medical_condition"].value_counts().head(10)
fig = px.bar(
    x=top_conditions.index,
    y=top_conditions.values,
    labels={'x': 'Condition', 'y': 'Patient Count'},
    title='Top 10 Medical Conditions',
    color_discrete_sequence=["skyblue"]
)
st.plotly_chart(fig, use_container_width=True)

# Hospital Ratings by Insurance Provider
st.markdown("### ⭐ Average Hospital Rating by Insurance Provider")
avg_rating = filtered_df.groupby("insurance_provider")["hospital_overall_rating"].mean().sort_values(ascending=False)
fig2 = px.bar(
    x=avg_rating.index,
    y=avg_rating.values,
    labels={'x': 'Insurance Provider', 'y': 'Avg Rating'},
    title='Average Hospital Rating',
    color_discrete_sequence=["skyblue"]
)
st.plotly_chart(fig2, use_container_width=True)

# Length of Stay Distribution
st.markdown("### \U0001F4C5 Length of Stay Distribution")
fig3, ax = plt.subplots()
sns.histplot(filtered_df["length_of_stay"].dropna(), bins=10, kde=True, color="purple", ax=ax)
ax.set_xlabel("Length of Stay (days)")
ax.set_ylabel("Number of Patients")
st.pyplot(fig3)

# Display filtered data
st.markdown("### \U0001F4CB Patient Data (Filtered)")
st.dataframe(filtered_df.head(100))

# Download button
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Filtered Data", convert_df_to_csv(filtered_df), "filtered_data.csv", "text/csv")

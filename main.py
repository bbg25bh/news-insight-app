import streamlit as st
from datetime import date

st.set_page_config(page_title="News Insight Generator", layout="centered")

st.title("📰 News Insight Generator")

st.markdown("Enter your search parameters below:")

# --- Input form
with st.form("news_input_form"):
    topic = st.text_input("Topic / Company / Industry", placeholder="e.g. Oncology Diagnostics India")
    region = st.text_input("Geography (optional)", placeholder="e.g. India, US, Southeast Asia")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date(2024, 7, 1))
    with col2:
        end_date = st.date_input("End Date", value=date(2024, 7, 15))
    
    submitted = st.form_submit_button("Run Analysis")

if submitted:
    st.success("✔️ Input received! Querying SerpAPI next...")
    st.write(f"🔎 **Query:** {topic} | 📍 Region: {region or 'Global'}")
    st.write(f"📅 **Date Range:** {start_date} to {end_date}")
    st.info("🛠️ Backend integration with SerpAPI & Gemini coming next.")

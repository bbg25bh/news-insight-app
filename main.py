import streamlit as st
import requests
import os
from datetime import date
from dotenv import load_dotenv

# Load SerpAPI key
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

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
    query = f"{topic} {region}".strip()
    st.write(f"🔎 Searching news for: **{query}**")
    
    params = {
        "engine": "google_news",
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": "en",
        "gl": "in",
        "num": 20,
        "tbs": f"cdr:1,cd_min:{start_date.strftime('%m/%d/%Y')},cd_max:{end_date.strftime('%m/%d/%Y')}"
    }

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    articles = data.get("news_results", [])
    if not articles:
        st.warning("No articles found for this search.")
    else:
        st.success(f"✅ Found {len(articles)} articles.")
        for article in articles:
            st.markdown(f"### [{article['title']}]({article['link']})")
            st.write(article.get("snippet", "No summary available."))
            st.caption(f"Published: {article.get('date', 'Unknown')} | Source: {article.get('source')}")

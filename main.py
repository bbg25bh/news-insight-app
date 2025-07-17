import streamlit as st
import requests
import os
from datetime import date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
BROWSERLESS_URL = os.getenv("BROWSERLESS_URL")

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

# --- Function to fetch full article content
def fetch_full_text(url):
    try:
        payload = {
            "url": url,
            "elements": [{"selector": "body"}],
            "gotoOptions": {"waitUntil": "networkidle2"}
        }
        response = requests.post(f"{BROWSERLESS_URL}/content", json=payload, timeout=30)
        data = response.json()
        return data.get("data", "")
    except Exception as e:
        return f"Error fetching article content: {e}"

# --- Logic triggered on form submit
if submitted:
    query_parts = [topic.strip()]
    if region.strip() and region.strip().lower() not in topic.strip().lower():
        query_parts.append(region.strip())

    query = " ".join(query_parts)
    st.write(f"🔎 Searching news for: **{query}**")

    # API call to SerpAPI
    params = {
        "engine": "google_news",
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": "en",
        "gl": "in",
        "num": 10,
        # "tbs": f"cdr:1,cd_min:{start_date.strftime('%m/%d/%Y')},cd_max:{end_date.strftime('%m/%d/%Y')}"
        # Remove custom date filter temporarily for testing
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
            st.caption(f"Published: {article.get('date', 'Unknown')} | Source: {article.get('source', {}).get('name', 'N/A')}")

            with st.spinner("🔍 Extracting full article..."):
                full_text = fetch_full_text(article['link'])
                st.write(full_text[:1000] + "..." if full_text else "No content extracted.")

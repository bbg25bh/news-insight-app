import streamlit as st
import requests
from datetime import date  # ✅ Fix 1: Needed for date inputs

# Load secrets
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
BROWSERLESS_TOKEN = st.secrets["BROWSERLESS_TOKEN"]

# --- Page setup
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

# --- Function to fetch full article content using Browserless
def fetch_full_text(url):
    try:
        api_url = f"https://production-sfo.browserless.io/content?token={BROWSERLESS_TOKEN}"
        payload = {
            "url": url,
            "gotoOptions": {
                "waitUntil": "domcontentloaded"  # safer value than networkidle2
            }
        }
        response = requests.post(api_url, json=payload, timeout=30)
        response.raise_for_status()

        # Safely attempt to parse JSON only if content is non-empty
        if not response.content:
            return "⚠️ Empty response from Browserless."

        try:
            data = response.json()
        except ValueError:
            return "❌ Failed to parse JSON. Possibly non-HTML response or site blocked scraping."

        content = data.get("data", "")
        return content.strip() if content.strip() else "⚠️ No article content found."

    except requests.exceptions.Timeout:
        return "❌ Timeout: Browserless request took too long."
    except requests.exceptions.HTTPError as http_err:
        return f"❌ HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"

# --- Main logic
if submitted:
    query_parts = [topic.strip()]
    if region.strip() and region.strip().lower() not in topic.strip().lower():
        query_parts.append(region.strip())

    query = " ".join(query_parts)
    st.write(f"🔎 Searching news for: **{query}**")

    # --- API call to SerpAPI
    params = {
        "engine": "google",
        "tbm": "nws",
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": "en",
        "gl": "in",
        "num": 10,
        # Optional: Uncomment for date filtering
        # "tbs": f"cdr:1,cd_min:{start_date.strftime('%m/%d/%Y')},cd_max:{end_date.strftime('%m/%d/%Y')}"
    }

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    # 🧪 TEMP: Show full response (optional - comment out when not needed)
    # st.json(data)

    articles = data.get("news_results", [])

    if not articles:
        st.warning("No articles found for this search.")
    else:
        st.success(f"✅ Found {len(articles)} articles.")
        for article in articles:
            st.markdown(f"### [{article['title']}]({article['link']})")
            source = article.get("source")
            source_name = source.get("name") if isinstance(source, dict) else source or "N/A"
            st.caption(f"Published: {article.get('date', 'Unknown')} | Source: {source_name}")

            with st.spinner("🔍 Extracting full article..."):
                full_text = fetch_full_text(article['link'])
                st.write(full_text[:1000] + "..." if full_text else "No content extracted.")

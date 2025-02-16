import streamlit as st
from pytrends.request import TrendReq
import random
import time

st.title("🔍 YouTube Keyword Finder (No YouTube API)")

# User input
keyword_input = st.text_input("Enter a seed keyword (in English) for YouTube:")
region = st.text_input("Enter Country Code (e.g., US, IN, GB) - optional:", "").strip().upper()

# Filters
min_interest = st.number_input("Minimum Interest Score (optional, 0 to ignore):", min_value=0, value=0)
max_results = st.number_input("Maximum Number of Keywords to Display:", min_value=1, value=20)

# If no keyword provided, pick a random one
random_keywords = ["technology", "gaming", "music", "vlog", "reviews", "tutorial", "comedy", "travel", "food", "fitness"]
if not keyword_input:
    keyword_input = random.choice(random_keywords)
    st.info(f"⚠️ No keyword provided. Using random keyword: **{keyword_input}**")

def fetch_keywords(seed_keyword):
    """Fetch YouTube-related keywords using Google Trends."""
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        geo = region if region else ""
        pytrends.build_payload([seed_keyword], timeframe='today 12-m', gprop='youtube', geo=geo)

        related = pytrends.related_queries().get(seed_keyword, {})
        keywords = []

        # Extract top queries
        if "top" in related and related["top"] is not None:
            top_df = related["top"]
            if min_interest > 0:
                top_df = top_df[top_df['value'] >= min_interest]
            keywords += top_df['query'].tolist()

        # Extract rising queries
        if "rising" in related and related["rising"] is not None:
            rising_df = related["rising"]
            keywords += rising_df['query'].tolist()

        return list(set(keywords))  # Remove duplicates

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return []

# Fetch and display keywords
if st.button("Find YouTube Keywords"):
    retries = 5  # Maximum retries for failed keywords
    attempts = 0
    keywords_found = []

    while attempts < retries and not keywords_found:
        keywords_found = fetch_keywords(keyword_input)
        if not keywords_found:
            st.warning(f"⚠️ No data for keyword '{keyword_input}'. Retrying with a new random keyword...")
            keyword_input = random.choice(random_keywords)
            time.sleep(2)  # Pause to avoid triggering rate limits
        attempts += 1

    if keywords_found:
        st.success(f"✅ Found {len(keywords_found)} keywords:")
        for kw in keywords_found[:max_results]:
            st.write(f"- {kw}")
    else:
        st.error("❌ No keywords found after multiple attempts. Please try again later.")

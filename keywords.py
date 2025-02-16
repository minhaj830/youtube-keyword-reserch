import streamlit as st
from pytrends.request import TrendReq
import random

st.title("YouTube Keyword Finder (No YouTube API Needed)")

# User input for a seed keyword specifically for YouTube
keyword_input = st.text_input("Enter a seed keyword (in English) for YouTube:")

# Optional filter: Minimum interest score (Google Trends score)
min_interest = st.number_input("Minimum Interest Score (optional, 0 to ignore):", min_value=0, value=50)

# Maximum number of keywords to display
max_results = st.number_input("Maximum Number of Keywords to Display:", min_value=1, value=20)

# If no keyword is provided, choose one randomly from a predefined list
if not keyword_input:
    random_keywords = ["technology", "gaming", "music", "vlog", "reviews", "tutorial", "comedy", "travel", "food", "fitness"]
    keyword_input = random.choice(random_keywords)
    st.info(f"No keyword provided. Using random keyword: **{keyword_input}**")

if st.button("Find YouTube Keywords"):
    try:
        # Initialize pytrends with YouTube property
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload([keyword_input], timeframe='today 12-m', gprop='youtube')
        
        # Get related queries for the given keyword
        related = pytrends.related_queries().get(keyword_input, {})
        
        keyword_list = []
        # Check if 'top' data is available
        if "top" in related and related["top"] is not None:
            top_df = related["top"]
            if min_interest:
                top_df = top_df[top_df['value'] >= min_interest]
            keyword_list.extend(top_df['query'].tolist())
        
        # Check if 'rising' data is available
        if "rising" in related and related["rising"] is not None:
            rising_df = related["rising"]
            keyword_list.extend(rising_df['query'].tolist())
        
        # Remove duplicates
        keyword_list = list(set(keyword_list))
        
        if not keyword_list:
            st.warning("⚠️ No related YouTube keywords found. Try another keyword or adjust filters.")
        else:
            st.success(f"✅ Found {len(keyword_list)} related YouTube keywords:")
            for kw in keyword_list[:max_results]:
                st.write(kw)

    except IndexError:
        st.error("❌ Error: No data available for the provided keyword. Please try a different one.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")

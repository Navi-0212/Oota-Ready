import streamlit as st
import requests
import pandas as pd

# API Configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

# Page Config
st.set_page_config(
    page_title="Oota Ready",
    page_icon="🍽️",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stApp {
        background-color: #FBF9F8;
    }
    .stButton>button {
        background-color: #FF6B35;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #E55A2B;
    }
    .stSelectbox>div>div>select {
        background-color: #F8F9FA;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div style='background: linear-gradient(135deg, #AB3500 0%, #FF6B35 50%, #B7102A 100%);
            padding: 60px 20px; border-radius: 20px; margin-bottom: 30px; position: relative; overflow: hidden;'>
    <div style='position: absolute; top: 20px; left: 10px; width: 256px; height: 256px; background: white; border-radius: 50%; opacity: 0.1;'></div>
    <div style='position: absolute; bottom: 20px; right: 20px; width: 384px; height: 384px; background: white; border-radius: 50%; opacity: 0.1;'></div>
    <div style='position: relative; z-index: 1;'>
        <h1 style='color: white; font-size: 48px; font-weight: bold; text-align: center; margin: 0; letter-spacing: -0.03em; line-height: 1.1;'>
            Discover Your Next Meal
        </h1>
        <p style='color: white; font-size: 20px; text-align: center; margin-top: 16px; opacity: 0.95; font-weight: 300;'>
            AI-powered restaurant recommendations tailored to your taste
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Fetch metadata
@st.cache_data(ttl=300)
def get_locations():
    try:
        response = requests.get(f"{API_BASE_URL}/api/locations", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return []
    except Exception as e:
        st.error(f"Error fetching locations: {e}")
        return []

@st.cache_data(ttl=300)
def get_cuisines():
    try:
        response = requests.get(f"{API_BASE_URL}/api/cuisines", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return []
    except Exception as e:
        st.error(f"Error fetching cuisines: {e}")
        return []

# Get Recommendations
def get_recommendations(preferences):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/recommendations",
            json=preferences,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            st.error(f"API returned status {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error getting recommendations: {e}")
        return []

# Search Form Container
st.markdown("""
<div style='background: white; padding: 32px; border-radius: 16px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15); margin-bottom: 24px;'>
""", unsafe_allow_html=True)

with st.container():
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        locations = get_locations()
        location = st.selectbox("📍 Location", [""] + locations, key="location")
    
    with col2:
        budget = st.selectbox("💰 Budget", ["Low", "Medium", "High"], key="budget")
    
    with col3:
        cuisines = get_cuisines()
        cuisine = st.selectbox("🍽️ Cuisine", [""] + cuisines, key="cuisine")
    
    with col4:
        search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# Advanced Options
col1, col2 = st.columns([3, 1])
with col1:
    min_rating = st.slider("⭐ Minimum Rating", 0.0, 5.0, 0.0, 0.5)
with col2:
    reset_clicked = st.button("🔄 Reset Filters", use_container_width=True)

# Handle Search
if search_clicked:
    if location and cuisine:
        with st.spinner("Finding the best restaurants for you..."):
            preferences = {
                "location": location,
                "budget": budget.lower(),
                "cuisine": cuisine,
                "min_rating": min_rating
            }
            recommendations = get_recommendations(preferences)
            st.session_state.recommendations = recommendations
            st.session_state.last_search = preferences
    else:
        st.warning("Please select location and cuisine")

# Handle Reset
if reset_clicked:
    if 'recommendations' in st.session_state:
        del st.session_state.recommendations
    if 'last_search' in st.session_state:
        del st.session_state.last_search
    st.rerun()

# Display Results
if 'recommendations' in st.session_state and st.session_state.recommendations:
    st.markdown("""
    <div style='background: white; padding: 24px; border-radius: 16px; margin-top: 32px; border: 1px solid #E0E0E0; box-shadow: 0 4px 20px rgba(51, 51, 51, 0.08);'>
        <div style='display: flex; align-items: flex-start; gap: 16px;'>
            <div style='flex-shrink: 0; width: 48px; height: 48px; background: #FFF5F0; border-radius: 50%; display: flex; align-items: center; justify-content: center;'>
                <span style='font-size: 24px;'>✨</span>
            </div>
            <div style='flex: 1;'>
                <h3 style='color: #FF6B35; margin: 0 0 8px 0; font-size: 18px; font-weight: 600;'>AI-Powered Recommendations</h3>
                <p style='color: #1B1C1C; margin: 0 0 8px 0; line-height: 1.6;'>Based on your preferences, here are the top recommendations</p>
                <p style='color: #594139; margin: 0; font-size: 14px;'>Found {} restaurant{} matching your preferences</p>
            </div>
        </div>
    </div>
    """.format(len(st.session_state.recommendations), 's' if len(st.session_state.recommendations) != 1 else ''), unsafe_allow_html=True)
    
    # Display restaurants in grid
    cols = st.columns(3)
    for idx, restaurant in enumerate(st.session_state.recommendations):
        with cols[idx % 3]:
            rank = idx + 1
            match_score = restaurant.get('match_score', 0)
            match_percentage = int(match_score * 100) if match_score else 0
            
            st.markdown(f"""
            <div style='background: white; padding: 24px; border-radius: 16px; margin: 10px 0; border: {2 if rank == 1 else 1}px solid {"#FF6B35" if rank == 1 else "#E0E0E0"}; box-shadow: {f"0 12px 40px rgba(255, 107, 53, 0.2)" if rank == 1 else "0 4px 20px rgba(51, 51, 51, 0.08)"}; position: relative; transition: all 0.3s ease;'>
                {rank == 1 and f"<div style='position: absolute; top: -12px; left: -12px; width: 40px; height: 40px; background: #FF6B35; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);'>{rank}</div>"}
                <div style='background: linear-gradient(135deg, #FF6B35 0%, #B7102A 100%); color: white; padding: 6px 12px; border-radius: 20px; display: inline-block; font-size: 11px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);'>
                    ✨ AI Recommended
                </div>
                <h3 style='color: #1B1C1C; margin: 12px 0 8px 0; font-size: 20px; font-weight: 700;'>{restaurant.get('name', 'N/A')}</h3>
                <p style='color: #594139; margin: 6px 0; font-size: 14px;'>📍 {restaurant.get('location', 'N/A')}</p>
                <p style='color: #594139; margin: 6px 0; font-size: 14px;'>🍽️ {restaurant.get('cuisine', 'N/A')}</p>
                <p style='color: #594139; margin: 6px 0; font-size: 14px;'>💰 ₹{restaurant.get('cost_for_two', 'N/A')} for two</p>
                <div style='display: flex; align-items: center; gap: 8px; margin: 8px 0;'>
                    <span style='color: #594139; font-size: 14px;'>⭐ {restaurant.get('rating', 'N/A')}</span>
                    {match_percentage > 0 and f"<span style='background: #FFF5F0; color: #FF6B35; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; border: 1px solid #FFE8D6;'>📈 {match_percentage}% Match</span>"}
                </div>
                {restaurant.get('llm_explanation') and f"<p style='color: #1B1C1C; margin: 16px 0 0 0; padding: 16px; background: #FFF5F0; border-radius: 12px; border: 1px solid #FFE8D6; font-size: 14px; line-height: 1.6;'><strong style='color: #FF6B35;'>Why we recommend this:</strong> {restaurant.get('llm_explanation')}</p>"}
            </div>
            """, unsafe_allow_html=True)
else:
    # Show empty state
    st.markdown("""
    <div style='background: white; padding: 48px; border-radius: 16px; text-align: center; margin-top: 32px; border: 1px solid #E0E0E0;'>
        <div style='font-size: 64px; margin-bottom: 16px;'>🍽️</div>
        <h3 style='color: #1B1C1C; margin: 0 0 8px 0; font-size: 20px; font-weight: 700;'>Ready to discover your next meal?</h3>
        <p style='color: #594139; margin: 0; font-size: 16px;'>Select your preferences above and click Search to get AI-powered restaurant recommendations</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 48px; padding: 24px; color: #594139; font-size: 14px;'>
    <p>© 2024 Oota Ready. AI-Powered Restaurant Recommendations.</p>
</div>
""", unsafe_allow_html=True)

# Deployment Guide

This document provides instructions for deploying the Oota Ready restaurant recommendation system.

## Current Architecture

The project currently uses:
- **Frontend**: React 18+ with TypeScript, TailwindCSS, shadcn/ui
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL (for restaurant data)
- **Cache**: Redis (for caching)
- **LLM**: Groq API for AI recommendations

## Deployment Options

### Option 1: Deploy Current Stack (React + FastAPI)

#### Frontend Deployment (React)

**Vercel** (Recommended for React)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from frontend directory
cd frontend
vercel
```

**Netlify**
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Build and deploy
cd frontend
npm run build
netlify deploy --prod
```

#### Backend Deployment (FastAPI)

**Render** (Recommended for FastAPI)
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example`

**Railway**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Database Deployment

**PostgreSQL**
- **Supabase**: Free tier available, easy setup
- **Neon**: Serverless PostgreSQL with free tier
- **Render PostgreSQL**: Integrated with Render deployment

**Redis**
- **Redis Cloud**: Free tier available
- **Upstash**: Serverless Redis with free tier
- **Render Redis**: Integrated with Render deployment

### Option 2: Streamlit Deployment (Alternative)

Since you mentioned Streamlit, here's how to convert and deploy as a Streamlit app:

#### Converting to Streamlit

Streamlit is a Python-based framework. To convert the current React+FastAPI app to Streamlit:

1. **Create Streamlit App Structure**
```python
# streamlit_app.py
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
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div style='background: linear-gradient(135deg, #AB3500 0%, #FF6B35 50%, #B7102A 100%);
            padding: 60px 20px; border-radius: 20px; margin-bottom: 30px;'>
    <h1 style='color: white; font-size: 48px; font-weight: bold; text-align: center; margin: 0;'>
        Discover Your Next Meal
    </h1>
    <p style='color: white; font-size: 20px; text-align: center; margin-top: 10px;'>
        AI-powered restaurant recommendations tailored to your taste
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch metadata
@st.cache_data(ttl=300)
def get_locations():
    try:
        response = requests.get(f"{API_BASE_URL}/api/locations")
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return []
    except:
        return []

@st.cache_data(ttl=300)
def get_cuisines():
    try:
        response = requests.get(f"{API_BASE_URL}/api/cuisines")
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return []
    except:
        return []

# Get Recommendations
def get_recommendations(preferences):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/recommendations",
            json=preferences
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return []
    except Exception as e:
        st.error(f"Error getting recommendations: {e}")
        return []

# Search Form
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        locations = get_locations()
        location = st.selectbox("Location", [""] + locations, key="location")
    
    with col2:
        budget = st.selectbox("Budget", ["Low", "Medium", "High"], key="budget")
    
    with col3:
        cuisines = get_cuisines()
        cuisine = st.selectbox("Cuisine", [""] + cuisines, key="cuisine")
    
    with col4:
        if st.button("🔍 Search", type="primary", use_container_width=True):
            if location and cuisine:
                with st.spinner("Finding the best restaurants for you..."):
                    preferences = {
                        "location": location,
                        "budget": budget.lower(),
                        "cuisine": cuisine,
                        "min_rating": 0
                    }
                    recommendations = get_recommendations(preferences)
                    st.session_state.recommendations = recommendations
            else:
                st.warning("Please select location and cuisine")

# Rating Slider
col1, col2 = st.columns([3, 1])
with col1:
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.5)
with col2:
    if st.button("Reset Filters"):
        st.session_state.clear()
        st.rerun()

# Display Results
if 'recommendations' in st.session_state and st.session_state.recommendations:
    st.markdown("""
    <div style='background: white; padding: 20px; border-radius: 15px; margin-top: 20px; border: 1px solid #E0E0E0;'>
        <h3 style='color: #FF6B35; margin: 0 0 10px 0;'>✨ AI-Powered Recommendations</h3>
        <p style='color: #1B1C1C; margin: 0;'>Based on your preferences, here are the top recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display restaurants in grid
    cols = st.columns(3)
    for idx, restaurant in enumerate(st.session_state.recommendations):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style='background: white; padding: 20px; border-radius: 15px; margin: 10px 0; border: 1px solid #E0E0E0; box-shadow: 0 4px 20px rgba(51, 51, 51, 0.08);'>
                <div style='background: linear-gradient(135deg, #FF6B35 0%, #B7102A 100%); color: white; padding: 5px 15px; border-radius: 20px; display: inline-block; font-size: 12px; margin-bottom: 10px;'>
                    ✨ AI Recommended
                </div>
                <h3 style='color: #1B1C1C; margin: 10px 0 5px 0;'>{restaurant.get('name', 'N/A')}</h3>
                <p style='color: #594139; margin: 5px 0;'>📍 {restaurant.get('location', 'N/A')}</p>
                <p style='color: #594139; margin: 5px 0;'>🍽️ {restaurant.get('cuisine', 'N/A')}</p>
                <p style='color: #594139; margin: 5px 0;'>💰 ₹{restaurant.get('cost_for_two', 'N/A')} for two</p>
                <p style='color: #594139; margin: 5px 0;'>⭐ {restaurant.get('rating', 'N/A')}</p>
                {restaurant.get('llm_explanation') and f"<p style='color: #1B1C1C; margin: 10px 0; padding: 10px; background: #FFF5F0; border-radius: 10px;'><strong>Why we recommend this:</strong> {restaurant.get('llm_explanation')}</p>"}
            </div>
            """, unsafe_allow_html=True)
```

2. **Create requirements.txt for Streamlit**
```txt
streamlit
requests
pandas
```

3. **Deploy to Streamlit Cloud**
```bash
# Install Streamlit CLI
pip install streamlit

# Test locally
streamlit run streamlit_app.py

# Deploy to Streamlit Cloud
# 1. Push code to GitHub
# 2. Go to https://share.streamlit.io
# 3. Connect your repository
# 4. Configure deployment
```

4. **Streamlit Cloud Configuration**
- Main file path: `streamlit_app.py`
- Python version: 3.9+
- Add secrets in Streamlit Cloud dashboard:
  - `API_BASE_URL`: Your FastAPI backend URL

### Option 3: Hybrid Approach (Streamlit Frontend + FastAPI Backend)

Keep the FastAPI backend and use Streamlit as the frontend:

1. Deploy backend to Render/Railway
2. Create Streamlit app that calls the backend API
3. Deploy Streamlit app to Streamlit Cloud
4. Configure Streamlit secrets with backend URL

## Environment Variables

For all deployment options, ensure these environment variables are configured:

```bash
# Backend
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port
GROQ_API_KEY=your_groq_api_key
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
REACT_APP_API_URL=https://your-backend-url.com
```

## Database Setup

### PostgreSQL Setup

**Using Supabase:**
1. Create a free account at https://supabase.com
2. Create a new project
3. Get connection string from Settings > Database
4. Run data ingestion script to populate database

**Using Neon:**
1. Create account at https://neon.tech
2. Create a new project
3. Get connection string
4. Populate with restaurant data

### Redis Setup

**Using Upstash:**
1. Create account at https://upstash.com
2. Create a new Redis database
3. Get REST URL and token
4. Configure in environment variables

## Data Ingestion

Before deployment, ensure the database is populated with restaurant data:

```bash
cd backend
python scripts/ingest_data.py
```

## Monitoring and Logging

### Backend Monitoring
- Use Sentry for error tracking
- Configure logging to send to external service
- Set up health check endpoint monitoring

### Frontend Monitoring
- Use Vercel Analytics (if using Vercel)
- Configure error tracking with Sentry
- Monitor performance metrics

## CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        run: |
          # Add Render deployment webhook
          curl -X POST $RENDER_WEBHOOK

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## Cost Estimation

### Free Tier Options
- **Frontend**: Vercel/Netlify (Free)
- **Backend**: Render (Free tier available)
- **Database**: Supabase/Neon (Free tier available)
- **Redis**: Upstash (Free tier available)

### Paid Options (if needed)
- **Backend**: $7-25/month depending on usage
- **Database**: $15-50/month depending on size
- **Redis**: $5-20/month depending on usage

## Security Considerations

1. **API Keys**: Never commit API keys to git
2. **Environment Variables**: Use platform-specific secret management
3. **CORS**: Configure CORS properly for production
4. **Rate Limiting**: Implement rate limiting on API endpoints
5. **HTTPS**: Ensure all endpoints use HTTPS
6. **Authentication**: Add authentication if needed for production

## Troubleshooting

### Common Issues

**Backend Connection Issues**
- Check if database and Redis are accessible
- Verify environment variables are set correctly
- Check firewall/security group settings

**Frontend Build Issues**
- Ensure all dependencies are installed
- Check for TypeScript errors
- Verify environment variables are configured

**Database Connection Issues**
- Verify connection string format
- Check if database is running
- Ensure database user has proper permissions

## Support

For deployment issues:
- Check platform-specific documentation
- Review logs in deployment dashboard
- Test locally before deploying
- Use platform-specific debugging tools

## Next Steps

1. Choose deployment option based on your needs
2. Set up required services (database, Redis)
3. Configure environment variables
4. Test deployment locally
5. Deploy to chosen platform
6. Monitor and optimize performance

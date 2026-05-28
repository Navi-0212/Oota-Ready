# Deployment Guide

This document provides instructions for deploying the Oota Ready restaurant recommendation system.

## Current Architecture

The project currently uses:
- **Frontend**: React 18+ with TypeScript, TailwindCSS, shadcn/ui
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL (for restaurant data)
- **Cache**: Redis (for caching)
- **LLM**: Groq API for AI recommendations

## Recommended Deployment Strategy

### Primary Deployment: Railway (Backend) + Vercel (Frontend)

This is the recommended deployment approach for the Oota Ready application:

- **Backend**: Railway (FastAPI + PostgreSQL + Redis)
- **Frontend**: Vercel (React + TypeScript)
- **Advantages**: Easy setup, free tiers available, seamless integration, automatic SSL

#### Backend Deployment on Railway

**Step 1: Prepare Backend for Railway**

1. Create a `railway.json` file in the backend directory:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health"
  }
}
```

2. Ensure `requirements.txt` includes all dependencies:
```txt
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
redis
python-dotenv
pydantic
pydantic-settings
datasets
pandas
groq
httpx
```

**Step 2: Deploy via Railway Dashboard**

1. Go to https://railway.app and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will automatically detect the Python project
5. Configure the service:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Step 3: Add PostgreSQL Database**

1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will provide a `DATABASE_URL` in the service variables
4. Copy this URL for your backend configuration

**Step 4: Add Redis Cache**

1. In your Railway project, click "New Service"
2. Select "Database" → "Redis"
3. Railway will provide a `REDIS_URL` in the service variables
4. Copy this URL for your backend configuration

**Step 5: Configure Environment Variables**

Add these environment variables in your Railway backend service:

```bash
# Database
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis
REDIS_URL=${{Redis.REDIS_URL}}
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}

# LLM API
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
LLM_MODEL=llama3-70b-8192
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# API Configuration
API_HOST=0.0.0.0
API_PORT=${PORT}

# CORS Configuration
CORS_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:3000
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Environment
ENVIRONMENT=production
DEBUG=false

# Cache
CACHE_ENABLED=true
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

**Step 6: Run Data Ingestion**

After deployment, you need to populate the database with restaurant data:

1. Go to your Railway backend service
2. Click "Console" to open a terminal
3. Run the ingestion script:
```bash
python scripts/ingest_data.py --no-cache
```

**Step 7: Get Backend URL**

1. Go to your Railway backend service
2. Copy the generated domain (e.g., `your-backend.railway.app`)
3. This will be your `API_BASE_URL` for the frontend

#### Frontend Deployment on Vercel

**Step 1: Prepare Frontend for Vercel**

1. Create a `vercel.json` file in the frontend directory:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "installCommand": "npm install"
}
```

2. Update `frontend/.env.production`:
```bash
VITE_API_URL=https://your-backend.railway.app
```

**Step 2: Deploy via Vercel Dashboard**

1. Go to https://vercel.com and sign up/login
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

**Step 3: Configure Environment Variables**

Add this environment variable in Vercel:

```bash
VITE_API_URL=https://your-backend.railway.app
```

**Step 4: Deploy**

1. Click "Deploy"
2. Vercel will build and deploy your frontend
3. Wait for the deployment to complete
4. Copy the generated domain (e.g., `your-frontend.vercel.app`)

**Step 5: Update CORS in Railway**

Go back to your Railway backend service and update the CORS origins:

```bash
CORS_ORIGINS=https://your-frontend.vercel.app
```

#### Alternative: Deploy via CLI

**Railway CLI**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
cd backend
railway init

# Add PostgreSQL
railway add postgresql

# Add Redis
railway add redis

# Deploy
railway up

# Get service URLs
railway domain
```

**Vercel CLI**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from frontend directory
cd frontend
vercel

# Production deployment
vercel --prod
```

### Alternative Deployment Options

If you prefer different platforms, here are alternative options:

#### Backend Alternatives

**Render**
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example`
5. Add PostgreSQL and Redis from Render marketplace

**Fly.io**
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch --dockerfile Dockerfile

# Add PostgreSQL
fly postgres create

# Deploy
fly deploy
```

#### Frontend Alternatives

**Netlify**
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Build and deploy
cd frontend
npm run build
netlify deploy --prod
```

**AWS Amplify**
1. Connect your GitHub repository
2. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. Add environment variables
4. Deploy

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

### Railway Backend Environment Variables

Configure these in your Railway backend service:

```bash
# Database (Railway provides this automatically)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (Railway provides this automatically)
REDIS_URL=${{Redis.REDIS_URL}}
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}

# LLM API (Required - get from Groq)
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
LLM_MODEL=llama3-70b-8192
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# API Configuration
API_HOST=0.0.0.0
API_PORT=${PORT}

# CORS Configuration (Update with your Vercel domain)
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Environment
ENVIRONMENT=production
DEBUG=false

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### Vercel Frontend Environment Variables

Configure these in your Vercel project settings:

```bash
# API URL (Update with your Railway backend domain)
VITE_API_URL=https://your-backend.railway.app
```

### Getting Groq API Key

1. Go to https://console.groq.com
2. Sign up for a free account
3. Navigate to API Keys
4. Create a new API key
5. Copy the key and add it to Railway environment variables

## Database Setup

### Railway PostgreSQL (Recommended)

When using Railway, PostgreSQL is automatically provisioned:

1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway automatically provides:
   - `DATABASE_URL` environment variable
   - Automatic backups
   - Connection pooling
   - SSL encryption

**Connection Details:**
- Railway provides the connection string automatically
- Access via `${{Postgres.DATABASE_URL}}` in environment variables
- No manual configuration needed

### Alternative PostgreSQL Options

If not using Railway:

**Supabase:**
1. Create a free account at https://supabase.com
2. Create a new project
3. Get connection string from Settings > Database
4. Run data ingestion script to populate database

**Neon:**
1. Create account at https://neon.tech
2. Create a new project
3. Get connection string
4. Populate with restaurant data

### Railway Redis (Recommended)

When using Railway, Redis is automatically provisioned:

1. In your Railway project, click "New Service"
2. Select "Database" → "Redis"
3. Railway automatically provides:
   - `REDIS_URL` environment variable
   - `REDIS_HOST` and `REDIS_PORT` variables
   - Automatic persistence
   - Connection pooling

**Connection Details:**
- Railway provides Redis connection details automatically
- Access via `${{Redis.REDIS_URL}}` in environment variables
- No manual configuration needed

### Alternative Redis Options

If not using Railway:

**Upstash:**
1. Create account at https://upstash.com
2. Create a new Redis database
3. Get REST URL and token
4. Configure in environment variables

## Data Ingestion

### Running Data Ingestion on Railway

After deploying your backend to Railway, populate the database with restaurant data:

1. Go to your Railway backend service
2. Click "Console" to open a web-based terminal
3. Run the ingestion script:
```bash
python scripts/ingest_data.py --no-cache
```

**Note:** Use `--no-cache` flag to skip Redis caching if Redis is not yet configured.

### Running Data Ingestion Locally

Alternatively, run ingestion locally before deployment:

```bash
cd backend
python scripts/ingest_data.py --no-cache
```

Then deploy to Railway with the pre-populated database.

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

### GitHub Actions for Railway + Vercel

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          npm i -g @railway/cli
          railway login --token ${{ secrets.RAILWAY_TOKEN }}
          cd backend
          railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: |
          npm i -g vercel
          cd frontend
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
```

### Required GitHub Secrets

Add these secrets to your GitHub repository:

- `RAILWAY_TOKEN`: Get from Railway account settings
- `VERCEL_TOKEN`: Get from Vercel account settings

### Automatic Deployments

**Railway:**
- Automatic deployments on push to main branch
- Can be configured in Railway dashboard
- Supports preview deployments for pull requests

**Vercel:**
- Automatic deployments on push to main branch
- Preview deployments for every branch/PR
- Can be configured in Vercel dashboard

## Cost Estimation

### Railway + Vercel Free Tier

**Railway Free Tier:**
- $5 free credit per month
- Includes:
  - 512MB RAM
  - Shared CPU
  - 1GB PostgreSQL storage
  - 1GB Redis storage
  - Sufficient for small to medium applications

**Vercel Free Tier:**
- Completely free for personal projects
- Includes:
  - Unlimited deployments
  - 100GB bandwidth per month
  - Automatic HTTPS
  - Global CDN
  - Preview deployments

**Total Cost: $0/month** (within free tier limits)

### Railway Paid Plans (if needed)

**Starter Plan ($5/month):**
- 1GB RAM
- Dedicated CPU
- 10GB PostgreSQL storage
- 10GB Redis storage

**Production Plan ($20/month):**
- 2GB RAM
- Dedicated CPU
- 50GB PostgreSQL storage
- 50GB Redis storage
- Priority support

### Vercel Paid Plans (if needed)

**Pro Plan ($20/month):**
- Unlimited bandwidth
- 1TB edge cache
- Team collaboration
- Advanced analytics

**Enterprise Plan (Custom):**
- Custom SLA
- Dedicated support
- SSO
- Advanced security

### Estimated Total Costs

**Development/Small Scale:**
- Frontend: $0 (Vercel Free)
- Backend: $0 (Railway Free)
- Database: $0 (Railway Free)
- Redis: $0 (Railway Free)
- **Total: $0/month**

**Production/Medium Scale:**
- Frontend: $0 (Vercel Free)
- Backend: $5-20 (Railway)
- Database: Included in Railway
- Redis: Included in Railway
- **Total: $5-20/month**

**Large Scale:**
- Frontend: $20 (Vercel Pro)
- Backend: $20+ (Railway Production)
- Database: Included in Railway
- Redis: Included in Railway
- **Total: $40+/month**

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

### Quick Start with Railway + Vercel

1. **Prepare Backend**
   - Create `railway.json` in backend directory
   - Ensure `requirements.txt` is complete
   - Push code to GitHub

2. **Deploy Backend to Railway**
   - Create Railway account at https://railway.app
   - Connect GitHub repository
   - Add PostgreSQL and Redis services
   - Configure environment variables
   - Deploy backend service

3. **Run Data Ingestion**
   - Open Railway console
   - Run `python scripts/ingest_data.py --no-cache`
   - Verify database is populated

4. **Prepare Frontend**
   - Create `vercel.json` in frontend directory
   - Update `.env.production` with Railway backend URL
   - Push code to GitHub

5. **Deploy Frontend to Vercel**
   - Create Vercel account at https://vercel.com
   - Connect GitHub repository
   - Configure environment variables
   - Deploy frontend service

6. **Update CORS**
   - Go back to Railway backend
   - Update `CORS_ORIGINS` with Vercel domain
   - Redeploy backend

7. **Test Deployment**
   - Visit your Vercel frontend URL
   - Test search functionality
   - Verify API calls work correctly

8. **Monitor and Optimize**
   - Set up Railway monitoring
   - Enable Vercel Analytics
   - Monitor performance metrics
   - Optimize as needed

### Additional Setup (Optional)

- **CI/CD**: Set up GitHub Actions for automatic deployments
- **Monitoring**: Configure Sentry for error tracking
- **Analytics**: Enable detailed analytics on both platforms
- **Custom Domain**: Add custom domains for production

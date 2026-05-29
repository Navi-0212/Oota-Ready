# Database Setup Guide for Bangalore Restaurant Data

This guide will help you set up the PostgreSQL database and populate it with Bangalore restaurant data including cuisines, menus, and prices from various areas.

## Prerequisites

1. **PostgreSQL** installed on your system
2. **Python 3.8+** installed
3. Database credentials (user, password, database name)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- sqlalchemy (ORM)
- psycopg2-binary (PostgreSQL adapter)
- python-dotenv (Environment variables)
- pydantic (Data validation)
- fastapi (Web framework)
- uvicorn (ASGI server)

## Step 2: Set Up PostgreSQL Database

### Option A: Using PostgreSQL directly

1. Create a database user:
```sql
CREATE USER zomato_user WITH PASSWORD 'zomato_pass';
```

2. Create a database:
```sql
CREATE DATABASE zomato OWNER zomato_user;
```

3. Grant privileges:
```sql
GRANT ALL PRIVILEGES ON DATABASE zomato TO zomato_user;
```

### Option B: Using Docker (Recommended)

```bash
docker run --name zomato-postgres \
  -e POSTGRES_USER=zomato_user \
  -e POSTGRES_PASSWORD=zomato_pass \
  -e POSTGRES_DB=zomato \
  -p 5432:5432 \
  -d postgres:15
```

## Step 3: Configure Environment Variables

The `.env` file is gitignored for security. Create it in the `backend/` directory:

```bash
cd backend
cp .env.example .env
```

Edit the `.env` file with your database credentials:

```env
# Database Configuration
DATABASE_URL=postgresql://zomato_user:zomato_pass@localhost:5432/zomato
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=zomato
DATABASE_USER=zomato_user
DATABASE_PASSWORD=zomato_pass
```

**Important**: Update the password and other values to match your PostgreSQL setup.

## Step 4: Run Data Ingestion Script

The ingestion script will:
- Create all database tables (areas, cuisines, restaurants, menu_items)
- Populate the database with sample Bangalore restaurant data
- Include 10+ areas across Bangalore
- Include 15+ cuisine types
- Include 10+ restaurants with detailed menus and prices

Run the script:

```bash
cd backend
python scripts/ingest_bangalore_data.py
```

### Expected Output

You should see:
```
INFO - Starting database initialization...
INFO - Database initialized successfully
INFO - Starting data ingestion...
INFO - Added area: Indiranagar
INFO - Added area: Koramangala
...
INFO - Added cuisine: North Indian
INFO - Added cuisine: South Indian
...
INFO - Added restaurant: Truffles with 5 menu items
INFO - Added restaurant: Meghana Foods with 5 menu items
...
INFO - Data ingestion completed successfully!

=== Database Summary ===
Areas: 10+
Cuisines: 15+
Restaurants: 10+
Menu Items: 50+
========================
```

## Step 5: Verify Database Connection

Start the FastAPI application:

```bash
cd backend
python -m app.main
```

Or using uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "recommendation-api"
}
```

## Database Schema

### Tables Created:

1. **areas** - Bangalore neighborhoods
   - id, name, city, pincode, description

2. **cuisines** - Cuisine types
   - id, name, description, origin

3. **restaurants** - Restaurant information
   - id, name, area_id, location, cuisine_id, cuisine, cost_for_two, rating, votes, reviews, address, phone, url, budget_category, rating_category

4. **menu_items** - Individual menu items with prices
   - id, restaurant_id, name, description, price, category, is_vegetarian, is_available

## Sample Data Included

### Areas (10+):
- Indiranagar, Koramangala, HSR Layout, Jayanagar, Whitefield, MG Road, Brigade Road, Electronic City, BTM Layout, Frazer Town

### Cuisines (15+):
- North Indian, South Indian, Chinese, Italian, Mexican, Thai, Japanese, Continental, Biryani, Kerala, Andhra, Mughlai, Seafood, Street Food, Cafe

### Restaurants (10+):
- Truffles (Continental, Indiranagar)
- Meghana Foods (Biryani, Jayanagar)
- Toit (Continental, Indiranagar)
- Vidyarthi Bhavan (South Indian, Basavanagudi)
- China Town (Chinese, Koramangala)
- Punjabi Rasoi (North Indian, Whitefield)
- Coastal Kitchen (Seafood, Frazer Town)
- Thai Me Up (Thai, HSR Layout)
- Sushi House (Japanese, MG Road)
- Chai Point (Cafe, Electronic City)

Each restaurant includes 5+ menu items with prices, categories, and vegetarian/non-vegetarian flags.

## Troubleshooting

### Connection Error
- Ensure PostgreSQL is running
- Verify DATABASE_URL in .env file
- Check firewall settings

### Table Creation Error
- Ensure database user has CREATE TABLE privileges
- Check if tables already exist (script will skip duplicates)

### Import Error
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

## Next Steps

After database setup:
1. The FastAPI app will automatically connect to the database on startup
2. You can query the database through the API endpoints
3. Add more restaurants and menu items using the ingestion script as a template
4. Extend the schema as needed for additional features

## API Endpoints

Once the database is set up, you can access:
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/recommendations` - Restaurant recommendations (requires query parameters)

See the API documentation for more details.

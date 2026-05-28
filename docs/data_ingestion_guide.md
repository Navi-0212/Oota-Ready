# Data Ingestion Guide

## Overview

This guide explains how to load, preprocess, and ingest restaurant data into the database for the AI-Powered Restaurant Recommendation System.

## Prerequisites

- Python 3.11+ installed
- PostgreSQL database running
- Redis cache running (optional but recommended)
- Environment variables configured in `backend/.env`

## Data Source

The restaurant data is sourced from Hugging Face:
- **Dataset**: [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- **Format**: Hugging Face Dataset
- **Size**: Varies (typically thousands of restaurant records)

## Ingestion Process

The data ingestion process consists of five main steps:

1. **Dataset Loading**: Load data from Hugging Face
2. **Data Preprocessing**: Clean and transform the data
3. **Database Initialization**: Set up database schema
4. **Data Ingestion**: Insert data into database
5. **Validation**: Verify data integrity

## Step-by-Step Guide

### Step 1: Configure Environment Variables

Create or update `backend/.env` with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://zomato_user:zomato_pass@localhost:5432/zomato
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=zomato
DATABASE_USER=zomato_user
DATABASE_PASSWORD=zomato_pass

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Step 2: Start Required Services

#### Using Docker Compose (Recommended)

```bash
docker-compose up -d postgres redis
```

#### Manual Setup

Start PostgreSQL:
```bash
# On Ubuntu/Debian
sudo systemctl start postgresql

# On macOS (using Homebrew)
brew services start postgresql
```

Start Redis:
```bash
# On Ubuntu/Debian
sudo systemctl start redis

# On macOS (using Homebrew)
brew services start redis
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Run Data Ingestion

#### Option A: Using the Ingestion Script (Recommended)

```bash
cd backend
python scripts/ingest_data.py
```

#### Option B: Using Command Line Arguments

```bash
python scripts/ingest_data.py --no-cache --batch-size 500
```

#### Available Arguments

- `--no-cache`: Disable dataset caching (force fresh download)
- `--no-save-local`: Don't save dataset locally
- `--batch-size`: Set batch size for insertion (default: 1000)

### Step 5: Verify Ingestion

Check the database to verify data was ingested successfully:

```bash
# Using psql
psql -U zomato_user -d zomato -c "SELECT COUNT(*) FROM restaurants;"

# Using Python
python -c "
from app.db.connection import get_database
from app.db.models import Restaurant
db = get_database()
with db.get_session() as session:
    count = session.query(Restaurant).count()
    print(f'Total restaurants: {count}')
"
```

## Ingestion Script Details

### Script Location
`backend/scripts/ingest_data.py`

### Script Functionality

The ingestion script performs the following operations:

1. **Load Dataset**
   - Attempts to load from Redis cache first (if enabled)
   - Falls back to Hugging Face API
   - Saves locally for future use (if enabled)
   - Handles network failures gracefully

2. **Preprocess Data**
   - Removes duplicate records
   - Handles missing values
   - Validates data types
   - Removes invalid records
   - Normalizes text fields
   - Standardizes location and cuisine names
   - Adds derived fields (budget_category, rating_category)

3. **Initialize Database**
   - Creates database schema if not exists
   - Tests database connection
   - Sets up indexes

4. **Ingest Data**
   - Clears existing data (optional)
   - Inserts data in batches
   - Implements retry logic for failed inserts
   - Tracks progress with progress bar
   - Logs errors for troubleshooting

5. **Validate Ingestion**
   - Compares record counts
   - Verifies data integrity
   - Reports success/failure statistics

### Error Handling

The script handles various error scenarios:

- **Network Failures**: Retries with exponential backoff
- **Dataset Errors**: Validates dataset before processing
- **Database Errors**: Implements transaction rollback
- **Invalid Data**: Skips invalid records with logging
- **Memory Issues**: Processes data in batches

## Manual Ingestion (Custom)

If you need to customize the ingestion process, you can use the Python API:

```python
from app.services.data_service import DataService
from app.services.data_preprocessor import DataPreprocessor
from app.db.connection import init_database
from app.db.models import Restaurant

# Initialize
data_service = DataService()
preprocessor = DataPreprocessor()
db = init_database()

# Load dataset
df = data_service.load_zomato_dataset(use_cache=True)

# Preprocess
df_clean = preprocessor.clean_data(df)
df_transformed = preprocessor.transform_data(df_clean)

# Validate
is_valid, errors = preprocessor.validate_data(df_transformed)
if not is_valid:
    print(f"Validation errors: {errors}")
    exit(1)

# Ingest
with db.get_session() as session:
    for _, row in df_transformed.iterrows():
        restaurant = Restaurant(
            name=row['name'],
            location=row['location'],
            cuisine=row['cuisine'],
            cost_for_two=float(row['cost_for_two']),
            rating=float(row['rating']),
            votes=int(row.get('votes', 0)),
            reviews=row.get('reviews', ''),
            address=row.get('address', ''),
            phone=row.get('phone', ''),
            url=row.get('url', ''),
            budget_category=row.get('budget_category', ''),
            rating_category=row.get('rating_category', '')
        )
        session.add(restaurant)
    session.commit()

print("Ingestion completed!")
```

## Troubleshooting

### Issue: Dataset Loading Fails

**Symptoms**: Error loading dataset from Hugging Face

**Solutions**:
1. Check internet connection
2. Verify Hugging Face API is accessible
3. Try with `--no-cache` flag
4. Check Hugging Face dataset status

### Issue: Database Connection Fails

**Symptoms**: Cannot connect to PostgreSQL

**Solutions**:
1. Verify PostgreSQL is running
2. Check connection string in `.env`
3. Verify database credentials
4. Check firewall settings

### Issue: Redis Connection Fails

**Symptoms**: Cannot connect to Redis cache

**Solutions**:
1. Verify Redis is running
2. Check Redis connection settings
3. Ingestion will continue without cache (warning logged)

### Issue: Memory Error During Ingestion

**Smptoms**: Out of memory error

**Solutions**:
1. Reduce batch size: `--batch-size 500`
2. Close other applications
3. Increase system memory
4. Process data in smaller chunks

### Issue: Duplicate Records

**Symptoms**: Duplicate restaurants in database

**Solutions**:
1. The script automatically removes duplicates based on (name, location)
2. Check preprocessing logs for duplicate removal statistics
3. Verify source data quality

### Issue: Invalid Data Records

**Symptoms**: Some records skipped during ingestion

**Solutions**:
1. Check logs for skipped record details
2. Verify data quality in source
3. Adjust validation rules if needed
4. Review preprocessing statistics

## Performance Optimization

### Batch Size Tuning

- **Default**: 1000 records per batch
- **For Low Memory**: Use 500 or lower
- **For High Memory**: Use 2000 or higher
- **Optimal**: Test different values to find best performance

### Caching Strategy

- **Dataset Cache**: 24 hours TTL in Redis
- **Metadata Cache**: 1 hour TTL for locations/cuisines
- **Disable Cache**: Use `--no-cache` for fresh data

### Database Optimization

- **Indexes**: Automatically created on common query columns
- **Connection Pooling**: Configured for 10 connections, 20 overflow
- **Query Optimization**: Use indexed columns in queries

## Monitoring

### Log Files

Ingestion logs are written to console with the following levels:
- INFO: Normal operations
- WARNING: Non-critical issues (e.g., cache miss)
- ERROR: Critical issues (e.g., database failure)

### Progress Tracking

The script displays progress using tqdm:
- Overall progress bar
- Batch insertion progress
- Success/error counts

### Statistics

After ingestion, the script reports:
- Initial record count
- Final record count
- Records removed (duplicates, invalid)
- Database record count
- Validation results

## Maintenance

### Regular Updates

To refresh data periodically:

```bash
# Weekly update
python scripts/ingest_data.py --no-cache

# Monthly update with validation
python scripts/ingest_data.py --no-cache --batch-size 500
```

### Data Quality Checks

Run validation after ingestion:

```bash
python -c "
from app.db.connection import get_database
from app.db.models import Restaurant
import pandas as pd

db = get_database()
with db.get_session() as session:
    # Check for nulls in required fields
    null_name = session.query(Restaurant).filter(Restaurant.name == None).count()
    null_location = session.query(Restaurant).filter(Restaurant.location == None).count()
    null_cuisine = session.query(Restaurant).filter(Restaurant.cuisine == None).count()
    
    print(f'Null names: {null_name}')
    print(f'Null locations: {null_location}')
    print(f'Null cuisines: {null_cuisine}')
"
```

### Cache Management

Clear cache if needed:

```bash
# Clear dataset cache
python -c "
from app.services.data_service import DataService
ds = DataService()
ds.clear_cache()
"
```

## Security Considerations

### Credentials
- Never commit `.env` file to version control
- Use strong passwords for database
- Rotate credentials regularly

### Data Privacy
- Review source dataset for sensitive information
- Ensure no PII is stored inadvertently
- Comply with data protection regulations

### Access Control
- Restrict database access to application only
- Use read-only users where possible
- Implement IP whitelisting for production

## Backup and Recovery

### Pre-Ingestion Backup

Before running ingestion, backup existing data:

```bash
# PostgreSQL backup
pg_dump -U zomato_user zomato > backup_$(date +%Y%m%d).sql

# Or use Docker
docker exec postgres pg_dump -U zomato_user zomato > backup.sql
```

### Post-Ingestion Verification

Verify data integrity after ingestion:

```bash
# Check record count
psql -U zomato_user -d zomato -c "SELECT COUNT(*) FROM restaurants;"

# Check data quality
psql -U zomato_user -d zomato -c "
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN rating < 0 OR rating > 5 THEN 1 END) as invalid_rating,
    COUNT(CASE WHEN cost_for_two <= 0 THEN 1 END) as invalid_cost
FROM restaurants;
"
```

### Recovery Procedure

If ingestion fails:

1. Restore from backup:
   ```bash
   psql -U zomato_user zomato < backup_20240101.sql
   ```

2. Re-run ingestion with smaller batch size:
   ```bash
   python scripts/ingest_data.py --batch-size 500
   ```

## Best Practices

1. **Test in Development**: Always test ingestion in development first
2. **Monitor Resources**: Watch memory and CPU usage during ingestion
3. **Use Caching**: Enable caching for faster subsequent runs
4. **Validate Data**: Always validate data after ingestion
5. **Keep Backups**: Maintain regular backups before major changes
6. **Document Changes**: Record any custom modifications to ingestion process
7. **Monitor Logs**: Review logs for warnings and errors
8. **Schedule Updates**: Set up automated periodic data refreshes

## Support

For issues or questions:
- Check logs for error details
- Review this troubleshooting guide
- Consult data_schema.md for schema details
- Open an issue in the project repository

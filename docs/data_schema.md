# Data Schema Documentation

## Overview

This document describes the database schema for the AI-Powered Restaurant Recommendation System, including the Restaurant table structure, indexes, and relationships.

## Database: PostgreSQL

The system uses PostgreSQL as the primary database for storing restaurant data.

## Table: restaurants

### Description
Stores restaurant information including name, location, cuisine, ratings, and other metadata.

### Columns

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each restaurant |
| name | String(255) | NOT NULL, INDEXED | Name of the restaurant |
| location | String(100) | NOT NULL, INDEXED | Location/city of the restaurant |
| cuisine | String(100) | NOT NULL, INDEXED | Cuisine type (e.g., Italian, Chinese) |
| cost_for_two | Float | NOT NULL | Average cost for two people |
| rating | Float | NOT NULL, INDEXED | Restaurant rating (0.0 - 5.0) |
| votes | Integer | DEFAULT 0 | Number of votes/ratings received |
| reviews | Text | NULLABLE | Customer reviews text |
| address | Text | NULLABLE | Full address of the restaurant |
| phone | String(20) | NULLABLE | Contact phone number |
| url | String(255) | NULLABLE | Website URL |
| budget_category | String(20) | NULLABLE | Derived budget category (low/medium/high) |
| rating_category | String(20) | NULLABLE | Derived rating category (excellent/very_good/good/average/below_average) |
| created_at | DateTime | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | DateTime | DEFAULT CURRENT_TIMESTAMP, ON UPDATE | Record last update timestamp |

### Indexes

#### Single Column Indexes
- `idx_name`: On `name` column for name-based searches
- `idx_location`: On `location` column for location filtering
- `idx_cuisine`: On `cuisine` column for cuisine filtering
- `idx_rating`: On `rating` column for rating-based queries

#### Composite Indexes
- `idx_location_cuisine`: On `(location, cuisine)` for combined location-cuisine queries
- `idx_location_rating`: On `(location, rating)` for location-based rating queries
- `idx_cuisine_rating`: On `(cuisine, rating)` for cuisine-based rating queries
- `idx_budget_rating`: On `(budget_category, rating)` for budget-based rating queries

### Constraints

#### Primary Key
- `id`: Auto-incrementing integer, unique identifier

#### Not Null Constraints
- `name`: Restaurant name is required
- `location`: Location is required
- `cuisine`: Cuisine type is required
- `cost_for_two`: Cost is required
- `rating`: Rating is required

#### Check Constraints (Implicit in Application Logic)
- `rating`: Must be between 0.0 and 5.0
- `cost_for_two`: Must be greater than 0

## Data Types

### String Types
- `String(255)`: Used for name, URL (up to 255 characters)
- `String(100)`: Used for location, cuisine (up to 100 characters)
- `String(20)`: Used for phone, budget_category, rating_category (up to 20 characters)
- `Text`: Used for reviews, address (unlimited length)

### Numeric Types
- `Integer`: Used for id, votes (whole numbers)
- `Float`: Used for cost_for_two, rating (decimal numbers)

### DateTime Types
- `DateTime`: Used for created_at, updated_at (timestamps)

## Derived Fields

### budget_category
Automatically calculated based on `cost_for_two`:
- **low**: cost_for_two ≤ 500
- **medium**: 500 < cost_for_two ≤ 1500
- **high**: cost_for_two > 1500

### rating_category
Automatically calculated based on `rating`:
- **excellent**: rating ≥ 4.5
- **very_good**: 4.0 ≤ rating < 4.5
- **good**: 3.5 ≤ rating < 4.0
- **average**: 3.0 ≤ rating < 3.5
- **below_average**: rating < 3.0

## Relationships

Currently, the schema has a single table (restaurants). Future enhancements may include:

### Potential Future Tables
- **users**: User accounts and preferences
- **user_reviews**: User-submitted reviews
- **bookings**: Restaurant reservation data
- **favorites**: User's favorite restaurants

### Potential Relationships
- users → user_reviews (one-to-many)
- restaurants → user_reviews (one-to-many)
- users → favorites (one-to-many)
- restaurants → favorites (one-to-many)

## ORM Model

The database schema is implemented using SQLAlchemy ORM in `backend/app/db/models.py`:

```python
class Restaurant(Base):
    __tablename__ = 'restaurants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(100), nullable=False, index=True)
    cuisine = Column(String(100), nullable=False, index=True)
    cost_for_two = Column(Float, nullable=False)
    rating = Column(Float, nullable=False, index=True)
    votes = Column(Integer, default=0)
    reviews = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    url = Column(String(255), nullable=True)
    budget_category = Column(String(20), nullable=True)
    rating_category = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Data Validation

### Application-Level Validation
Data validation is performed at the application level before insertion:
- Required fields validation
- Data type validation
- Range validation (rating 0-5, cost > 0)
- Text normalization and standardization

### Database-Level Validation
- Primary key uniqueness
- Not null constraints
- Index-based query optimization

## Performance Considerations

### Query Optimization
- Indexes on frequently queried columns (location, cuisine, rating)
- Composite indexes for common query patterns
- Connection pooling (pool_size=10, max_overflow=20)

### Caching Strategy
- Redis caching for frequently accessed data
- Cache keys:
  - `zomato:dataset:cached` - Full dataset cache
  - `zomato:locations` - Available locations
  - `zomato:cuisines` - Available cuisines
- TTL: 24 hours for dataset, 1 hour for metadata

## Migration Strategy

### Initial Setup
- Database tables are created automatically on first run using SQLAlchemy
- See `backend/app/db/connection.py` for initialization logic

### Future Migrations
- Use Alembic for database migrations
- Migration scripts in `backend/app/db/migrations/`
- Version control for schema changes

## Backup and Recovery

### Backup Strategy
- Regular automated backups (daily)
- Point-in-time recovery capability
- Backup retention policy (30 days)

### Recovery Procedure
1. Stop application
2. Restore from latest backup
3. Verify data integrity
4. Restart application

## Security Considerations

### Access Control
- Database credentials stored in environment variables
- Read-only user for application queries
- Restricted access to production database

### Data Privacy
- No personal user data stored in current schema
- Phone numbers and addresses are optional fields
- Reviews are anonymized (if implemented)

## Monitoring

### Performance Metrics
- Query execution time
- Index usage statistics
- Connection pool utilization
- Cache hit/miss ratios

### Alerts
- Slow query alerts (> 1 second)
- Connection pool exhaustion
- Cache failure alerts

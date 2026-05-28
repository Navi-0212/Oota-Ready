# System Architecture: AI-Powered Restaurant Recommendation System

## 1. Architecture Overview

The system follows a **microservices-inspired architecture** with clear separation of concerns across four main layers:

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│                    (Web Interface)                          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
┌────────────────────────▼────────────────────────────────────┐
│                   API Gateway Layer                         │
│              (Request Validation & Routing)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Backend Services Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Data       │  │  Filtering   │  │  LLM         │     │
│  │   Service    │  │  Service     │  │  Service     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Restaurant  │  │  Vector      │  │  Cache       │     │
│  │  Database    │  │  Store       │  │  (Redis)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## 2. Component Breakdown

### 2.1 Frontend Layer
**Technology**: React.js + TailwindCSS + shadcn/ui

**Responsibilities**:
- User preference collection form
- Display recommendation results
- Real-time UI updates
- Error handling and user feedback

**Key Components**:
- `PreferenceForm`: Collects location, budget, cuisine, rating, additional preferences
- `RecommendationCard`: Displays individual restaurant recommendations
- `ResultsContainer`: Manages list of recommendations
- `LoadingSpinner`: Shows during async operations

### 2.2 API Gateway Layer
**Technology**: FastAPI (Python) or Express.js (Node.js)

**Responsibilities**:
- Request validation
- Authentication/Authorization (if needed)
- Rate limiting
- Request routing to backend services
- Response formatting

**Endpoints**:
- `POST /api/recommendations`: Main recommendation endpoint
- `GET /api/health`: Health check
- `GET /api/locations`: Get available locations
- `GET /api/cuisines`: Get available cuisines

### 2.3 Backend Services Layer

#### 2.3.1 Data Service
**Technology**: Python (pandas, datasets library)

**Responsibilities**:
- Load dataset from Hugging Face
- Data preprocessing and cleaning
- Data caching in memory
- Schema validation

**Key Functions**:
- `load_dataset()`: Fetches data from Hugging Face
- `preprocess_data()`: Cleans and normalizes data
- `get_restaurant_by_id()`: Retrieves single restaurant
- `get_all_restaurants()`: Returns full dataset

#### 2.3.2 Filtering Service
**Technology**: Python

**Responsibilities**:
- Filter restaurants based on user preferences
- Apply budget constraints
- Apply rating thresholds
- Apply location and cuisine filters
- Rank filtered results

**Key Functions**:
- `filter_by_location(restaurants, location)`
- `filter_by_budget(restaurants, budget)`
- `filter_by_cuisine(restaurants, cuisine)`
- `filter_by_rating(restaurants, min_rating)`
- `apply_additional_filters(restaurants, preferences)`
- `rank_restaurants(restaurants)`

#### 2.3.3 LLM Service
**Technology**: Python (Groq API)

**Responsibilities**:
- Generate personalized recommendations
- Provide explanations for each recommendation
- Rank restaurants based on nuanced preferences
- Summarize choices

**Key Functions**:
- `generate_recommendations(filtered_data, user_preferences)`
- `generate_explanation(restaurant, user_preferences)`
- `rank_with_llm(restaurants, user_preferences)`
- `summarize_recommendations(recommendations)`

### 2.4 Data Layer

#### 2.4.1 Restaurant Database
**Technology**: PostgreSQL or SQLite (for development)

**Schema**:
```sql
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(100) NOT NULL,
    cuisine VARCHAR(100) NOT NULL,
    cost_for_two DECIMAL(10, 2),
    rating DECIMAL(3, 2) CHECK (rating >= 0 AND rating <= 5),
    votes INTEGER,
    reviews TEXT,
    address TEXT,
    phone VARCHAR(20),
    url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_location ON restaurants(location);
CREATE INDEX idx_cuisine ON restaurants(cuisine);
CREATE INDEX idx_rating ON restaurants(rating);
CREATE INDEX idx_cost ON restaurants(cost_for_two);
```

#### 2.4.2 Vector Store (Optional for Advanced Search)
**Technology**: Pinecone, Weaviate, or ChromaDB

**Purpose**: Store embeddings for semantic search on restaurant descriptions

#### 2.4.3 Cache Layer
**Technology**: Redis

**Purpose**: Cache frequent queries and LLM responses to reduce API calls

**Cache Keys**:
- `recommendations:{location}:{budget}:{cuisine}:{rating}` - Cached recommendation results
- `llm_response:{hash}` - Cached LLM responses
- `dataset:version` - Dataset version tracking

## 3. Data Flow

### 3.1 Recommendation Request Flow

```
User Input
    ↓
Frontend Validation
    ↓
POST /api/recommendations
    ↓
API Gateway (Validate Request)
    ↓
Filtering Service
    ├─→ Data Service (Load Dataset)
    ├─→ Apply Filters (Location, Budget, Cuisine, Rating)
    └─→ Rank Results
    ↓
LLM Service
    ├─→ Generate Explanations
    ├─→ Re-rank with LLM
    └─→ Summarize
    ↓
API Gateway (Format Response)
    ↓
Frontend Display
```

### 3.2 Data Ingestion Flow

```
Hugging Face Dataset
    ↓
Data Service
    ├─→ Download Dataset
    ├─→ Validate Schema
    ├─→ Clean Data
    ├─→ Transform to Database Schema
    └─→ Load into Database
    ↓
Database
```

## 4. Technology Stack

### 4.1 Frontend
- **Framework**: React 18+ with TypeScript
- **Styling**: TailwindCSS
- **UI Components**: shadcn/ui
- **State Management**: React Context API or Zustand
- **HTTP Client**: Axios or Fetch API
- **Icons**: Lucide React

### 4.2 Backend
- **API Framework**: FastAPI (Python) or Express.js (Node.js)
- **Data Processing**: pandas, numpy
- **Dataset Loading**: Hugging Face datasets library
- **LLM Integration**: Groq API
- **Async Processing**: asyncio (Python)

### 4.3 Database & Storage
- **Primary Database**: PostgreSQL (production) / SQLite (development)
- **Caching**: Redis
- **Vector Store** (optional): Pinecone or ChromaDB
- **Dataset Source**: Hugging Face Datasets

### 4.4 DevOps & Deployment
- **Containerization**: Docker
- **Orchestration**: Docker Compose (development)
- **Environment Management**: .env files
- **API Documentation**: Swagger/OpenAPI (FastAPI auto-generates)

## 5. API Specification

### 5.1 POST /api/recommendations

**Request Body**:
```json
{
  "location": "Delhi",
  "budget": "medium",
  "cuisine": "Italian",
  "min_rating": 4.0,
  "additional_preferences": "family-friendly, outdoor seating"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "id": 1,
        "name": "Restaurant Name",
        "cuisine": "Italian",
        "location": "Delhi",
        "rating": 4.5,
        "cost_for_two": 1500,
        "explanation": "This restaurant is perfect for your preferences because...",
        "match_score": 0.95
      }
    ],
    "summary": "Based on your preferences for Italian cuisine in Delhi with a medium budget...",
    "total_results": 10,
    "filters_applied": {
      "location": "Delhi",
      "budget": "medium",
      "cuisine": "Italian",
      "min_rating": 4.0
    }
  },
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "processing_time_ms": 250
  }
}
```

### 5.2 GET /api/locations

**Response**:
```json
{
  "success": true,
  "data": {
    "locations": ["Delhi", "Bangalore", "Mumbai", "Chennai", "Hyderabad"]
  }
}
```

### 5.3 GET /api/cuisines

**Response**:
```json
{
  "success": true,
  "data": {
    "cuisines": ["Italian", "Chinese", "Indian", "Mexican", "Thai", "Japanese"]
  }
}
```

## 6. LLM Integration Strategy

### 6.1 Prompt Engineering

**System Prompt**:
```
You are a restaurant recommendation expert. Your task is to analyze user preferences and restaurant data to provide personalized, helpful recommendations. Consider factors like cuisine, budget, location, ratings, and any additional preferences mentioned by the user.
```

**User Prompt Template**:
```
User Preferences:
- Location: {location}
- Budget: {budget}
- Cuisine: {cuisine}
- Minimum Rating: {min_rating}
- Additional Preferences: {additional_preferences}

Available Restaurants:
{restaurant_data}

Please:
1. Rank these restaurants based on how well they match the user's preferences
2. Provide a brief explanation for each recommendation (2-3 sentences)
3. Summarize the top 3 recommendations with key highlights
```

### 6.2 LLM Configuration

**Model Selection**:
- **Primary**: Groq LLaMA 3 70B or Mixtral 8x7B (best quality)
- **Fallback**: Groq LLaMA 3 8B or Gemma 7B (faster, cheaper)

**Parameters**:
- Temperature: 0.7 (balanced creativity)
- Max Tokens: 1000 (sufficient for explanations)
- Top P: 0.9

### 6.3 Caching Strategy

- Cache LLM responses for identical user preferences
- TTL: 24 hours
- Cache key based on hash of user preferences + filtered restaurant IDs

## 7. Security Considerations

### 7.1 API Security
- Rate limiting (100 requests/minute per IP)
- Input validation on all endpoints
- SQL injection prevention (parameterized queries)
- CORS configuration for frontend domain

### 7.2 LLM API Security
- Store API keys in environment variables
- Never expose API keys in frontend code
- Implement request quotas to control costs
- Sanitize user input before sending to LLM

### 7.3 Data Privacy
- No personal data collection
- Anonymous usage analytics (optional)
- Clear privacy policy

## 8. Performance Optimization

### 8.1 Database Optimization
- Indexes on frequently queried columns (location, cuisine, rating)
- Query optimization with EXPLAIN ANALYZE
- Connection pooling

### 8.2 Caching Strategy
- Redis cache for frequent queries
- Dataset caching in memory (Data Service)
- LLM response caching

### 8.3 Async Processing
- Async I/O for database operations
- Async LLM API calls
- Background job for dataset updates

## 9. Scalability Considerations

### 9.1 Horizontal Scaling
- Stateless API design enables easy scaling
- Load balancer for multiple API instances
- Database read replicas for read-heavy workloads

### 9.2 Vertical Scaling
- Monitor CPU, memory, and disk usage
- Optimize database queries
- Implement pagination for large result sets

### 9.3 Future Enhancements
- Add user authentication for personalized history
- Implement collaborative filtering
- Add image recognition for food photos
- Real-time availability integration
- Mobile app development

## 10. Development Phases

### Phase 1: MVP (Minimum Viable Product)
- Basic frontend with preference form
- Simple filtering without LLM
- Static dataset loading
- Basic recommendation display

### Phase 2: LLM Integration
- Integrate LLM API
- Generate explanations
- Implement ranking with LLM
- Add caching layer

### Phase 3: Production Ready
- Database implementation
- API documentation
- Error handling and logging
- Performance optimization
- Security hardening

### Phase 4: Advanced Features
- User accounts and preferences history
- Advanced semantic search with vector embeddings
- Real-time availability
- Mobile responsive design improvements
- A/B testing for recommendation algorithms

# Edge Cases and Error Handling: AI-Powered Restaurant Recommendation System

## 1. Data-Related Edge Cases

### 1.1 Empty Dataset
**Scenario**: Dataset from Hugging Face is empty or contains no records.

**Detection**:
- Check dataset length after loading
- Validate row count > 0

**Handling Strategy**:
```python
if len(dataset) == 0:
    raise DatasetEmptyError("No restaurant data available")
```
**Fallback**: Display user-friendly message, log error, alert admin
**User Message**: "We're currently experiencing issues with our restaurant database. Please try again later."

### 1.2 Missing Required Fields
**Scenario**: Records missing critical fields (name, location, cuisine, rating, cost).

**Detection**:
- Schema validation during preprocessing
- Check for null/None values in required columns

**Handling Strategy**:
```python
required_fields = ['name', 'location', 'cuisine', 'rating', 'cost_for_two']
for field in required_fields:
    if field not in df.columns or df[field].isnull().any():
        raise SchemaError(f"Missing or null required field: {field}")
```
**Fallback**: Skip invalid records, log warnings, continue with valid data
**User Message**: "Some restaurants couldn't be loaded due to incomplete data."

### 1.3 Invalid Data Types
**Scenario**: Rating is string instead of float, cost is negative, etc.

**Detection**:
- Type checking during preprocessing
- Range validation (rating 0-5, cost > 0)

**Handling Strategy**:
```python
# Convert and validate
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df = df[(df['rating'] >= 0) & (df['rating'] <= 5)]
df['cost_for_two'] = pd.to_numeric(df['cost_for_two'], errors='coerce')
df = df[df['cost_for_two'] > 0]
```
**Fallback**: Drop invalid records, log statistics
**User Message**: None (silent handling)

### 1.4 Duplicate Records
**Scenario**: Same restaurant appears multiple times in dataset.

**Detection**:
- Check for duplicate (name, location) combinations
- Count duplicates

**Handling Strategy**:
```python
duplicates = df.duplicated(subset=['name', 'location'], keep='first')
if duplicates.any():
    df = df[~duplicates]
    logger.warning(f"Removed {duplicates.sum()} duplicate records")
```
**Fallback**: Keep first occurrence, remove duplicates
**User Message**: None (silent handling)

### 1.5 Dataset Download Failure
**Scenario**: Hugging Face API is down or dataset is unavailable.

**Detection**:
- Catch network errors during dataset loading
- Timeout handling

**Handling Strategy**:
```python
try:
    dataset = load_dataset("ManikaSaini/zomato-restaurant-recommendation")
except (ConnectionError, TimeoutError) as e:
    raise DatasetLoadError(f"Failed to load dataset: {str(e)}")
```
**Fallback**: Use cached dataset if available, otherwise show error
**User Message**: "Unable to load restaurant data. Please check your internet connection."

### 1.6 Corrupted Data
**Scenario**: Data contains special characters, encoding issues, or malformed JSON.

**Detection**:
- Encoding validation
- JSON parsing errors
- Character encoding checks

**Handling Strategy**:
```python
try:
    df = pd.read_json(data)
except json.JSONDecodeError:
    raise DataCorruptionError("Dataset contains corrupted data")
```
**Fallback**: Attempt to clean data, skip corrupted records
**User Message**: "Some restaurant data couldn't be processed."

## 2. User Input Edge Cases

### 2.1 Empty or Null Input Fields
**Scenario**: User submits form with empty required fields.

**Detection**:
- Frontend validation
- Backend validation

**Handling Strategy**:
```python
if not location or not cuisine:
    raise ValidationError("Location and cuisine are required")
```
**Fallback**: Return 400 Bad Request with field-specific errors
**User Message**: "Please fill in all required fields."

### 2.2 Invalid Location
**Scenario**: User enters location not in dataset (e.g., "Mars", "Atlantis").

**Detection**:
- Check against available locations
- Fuzzy matching for typos

**Handling Strategy**:
```python
available_locations = get_available_locations()
if location not in available_locations:
    # Try fuzzy matching
    matched = fuzzy_match(location, available_locations)
    if matched:
        return {"warning": f"Did you mean {matched}?", "suggested_location": matched}
    else:
        raise ValidationError(f"Location '{location}' not found")
```
**Fallback**: Suggest closest match, show available locations
**User Message**: "Location not found. Did you mean [suggestion]?"

### 2.3 Invalid Cuisine
**Scenario**: User enters cuisine not in dataset (e.g., "Martian", "Fusion").

**Detection**:
- Check against available cuisines
- Case-insensitive comparison

**Handling Strategy**:
```python
available_cuisines = get_available_cuisines()
if cuisine.lower() not in [c.lower() for c in available_cuisines]:
    raise ValidationError(f"Cuisine '{cuisine}' not available")
```
**Fallback**: Show available cuisines, suggest similar cuisines
**User Message**: "Cuisine not available. Here are the available options: [list]"

### 2.4 Invalid Rating Range
**Scenario**: User enters rating outside 0-5 range (e.g., 6, -1, 10).

**Detection**:
- Range validation
- Type checking

**Handling Strategy**:
```python
if not (0 <= min_rating <= 5):
    raise ValidationError("Rating must be between 0 and 5")
```
**Fallback**: Clamp to valid range or reject
**User Message**: "Rating must be between 0 and 5."

### 2.5 Invalid Budget Category
**Scenario**: User enters invalid budget (e.g., "expensive", "free", "million").

**Detection**:
- Check against allowed values (low, medium, high)
- Case-insensitive comparison

**Handling Strategy**:
```python
valid_budgets = ['low', 'medium', 'high']
if budget.lower() not in valid_budgets:
    raise ValidationError(f"Budget must be one of: {valid_budgets}")
```
**Fallback**: Show valid options
**User Message**: "Budget must be low, medium, or high."

### 2.6 Extremely Long Additional Preferences
**Scenario**: User submits 10,000 characters in additional preferences.

**Detection**:
- Length validation
- Character limit enforcement

**Handling Strategy**:
```python
MAX_PREFERENCES_LENGTH = 500
if len(additional_preferences) > MAX_PREFERENCES_LENGTH:
    raise ValidationError(f"Preferences too long (max {MAX_PREFERENCES_LENGTH} characters)")
```
**Fallback**: Truncate or reject
**User Message**: "Preferences too long. Please keep it under 500 characters."

### 2.7 SQL Injection Attempts
**Scenario**: User enters malicious SQL in input fields.

**Detection**:
- Input sanitization
- Pattern matching for SQL keywords

**Handling Strategy**:
```python
dangerous_patterns = ['DROP', 'DELETE', 'UNION', 'SELECT', 'INSERT']
for pattern in dangerous_patterns:
    if pattern.lower() in input_string.lower():
        raise SecurityError("Invalid input detected")
```
**Fallback**: Reject request, log security event
**User Message**: "Invalid input detected."

### 2.8 XSS Attempts
**Scenario**: User enters script tags or malicious HTML.

**Detection**:
- HTML tag detection
- Script tag filtering

**Handling Strategy**:
```python
import re
if re.search(r'<script|<iframe|javascript:', input_string, re.IGNORECASE):
    raise SecurityError("Invalid input detected")
```
**Fallback**: Sanitize input or reject
**User Message**: "Invalid input detected."

## 3. Filtering Edge Cases

### 3.1 No Results After Filtering
**Scenario**: Filters are too restrictive, returning zero restaurants.

**Detection**:
- Check filtered result count
- Validate > 0 before proceeding

**Handling Strategy**:
```python
filtered = apply_filters(restaurants, preferences)
if len(filtered) == 0:
    return {
        "success": False,
        "message": "No restaurants match your criteria",
        "suggestions": relax_filters(preferences)
    }
```
**Fallback**: Suggest relaxing filters, show closest matches
**User Message**: "No restaurants match your exact criteria. Try relaxing your filters."

### 3.2 Too Many Results
**Scenario**: Filters are too broad, returning thousands of restaurants.

**Detection**:
- Check result count
- Set maximum limit (e.g., 100)

**Handling Strategy**:
```python
MAX_RESULTS = 100
if len(filtered) > MAX_RESULTS:
    filtered = filtered.head(MAX_RESULTS)
    logger.warning(f"Results truncated to {MAX_RESULTS}")
```
**Fallback**: Return top N results, suggest more specific filters
**User Message**: "Showing top 100 results. Try adding more filters for better results."

### 3.3 Ambiguous Budget Ranges
**Scenario**: "Medium" budget interpretation varies by location.

**Detection**:
- Check budget distribution per location
- Dynamic budget thresholds

**Handling Strategy**:
```python
# Calculate location-specific budget ranges
location_budgets = df.groupby('location')['cost_for_two'].describe()
low_threshold = location_budgets.loc[location, '25%']
high_threshold = location_budgets.loc[location, '75%']
```
**Fallback**: Use location-specific percentiles
**User Message**: None (transparent handling)

### 3.4 Rating Distribution Skew
**Scenario**: All restaurants have high ratings (4.5+), making min_rating filter ineffective.

**Detection**:
- Analyze rating distribution
- Check filter effectiveness

**Handling Strategy**:
```python
rating_distribution = df['rating'].describe()
if rating_distribution['min'] >= min_rating:
    logger.warning(f"Min rating filter {min_rating} is below dataset minimum")
```
**Fallback**: Warn user, suggest higher threshold
**User Message**: "All restaurants meet your rating criteria. Consider a higher rating threshold."

### 3.5 Cuisine with Few Options
**Scenario**: User selects rare cuisine with only 1-2 restaurants.

**Detection**:
- Count restaurants per cuisine
- Flag low-count cuisines

**Handling Strategy**:
```python
cuisine_count = df[df['cuisine'] == cuisine].shape[0]
if cuisine_count < 3:
    return {
        "warning": f"Only {cuisine_count} {cuisine} restaurants available",
        "suggestion": "Try a more common cuisine"
    }
```
**Fallback**: Warn user, suggest alternatives
**User Message**: "Only 2 Italian restaurants available. You might want to try other cuisines."

## 4. LLM Integration Edge Cases

### 4.1 LLM API Key Missing or Invalid
**Scenario**: API key not configured or expired.

**Detection**:
- Check environment variable
- Validate API key format

**Handling Strategy**:
```python
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise LLMConfigError("API key not configured")
```
**Fallback**: Use fallback ranking algorithm, alert admin
**User Message**: "AI recommendations temporarily unavailable. Showing standard results."

### 4.2 LLM API Rate Limit Exceeded
**Scenario**: Too many requests to LLM API, hitting rate limits.

**Detection**:
- Catch 429 Too Many Requests errors
- Implement exponential backoff

**Handling Strategy**:
```python
try:
    response = openai.ChatCompletion.create(...)
except openai.error.RateLimitError:
    # Use cached response or fallback
    return fallback_ranking(restaurants)
```
**Fallback**: Use cached results or simple ranking, retry with backoff
**User Message**: "AI recommendations temporarily unavailable. Showing cached results."

### 4.3 LLM API Timeout
**Scenario**: LLM API takes too long to respond.

**Detection**:
- Set timeout (e.g., 30 seconds)
- Catch timeout exceptions

**Handling Strategy**:
```python
try:
    response = openai.ChatCompletion.create(..., timeout=30)
except TimeoutError:
    return fallback_ranking(restaurants)
```
**Fallback**: Use simple ranking algorithm
**User Message**: "AI recommendation service is slow. Showing standard results."

### 4.4 LLM Returns Invalid JSON
**Scenario**: LLM returns malformed JSON or unexpected format.

**Detection**:
- JSON validation
- Schema validation

**Handling Strategy**:
```python
try:
    result = json.parse(llm_response)
except json.JSONDecodeError:
    logger.error("LLM returned invalid JSON")
    return fallback_ranking(restaurants)
```
**Fallback**: Use fallback ranking, log error for debugging
**User Message**: None (transparent fallback)

### 4.5 LLM Returns Empty Response
**Scenario**: LLM returns empty string or no content.

**Detection**:
- Check response length
- Validate content exists

**Handling Strategy**:
```python
if not llm_response or len(llm_response.strip()) == 0:
    logger.warning("LLM returned empty response")
    return fallback_ranking(restaurants)
```
**Fallback**: Use fallback ranking
**User Message**: None (transparent fallback)

### 4.6 LLM Cost Limit Exceeded
**Scenario**: Monthly API cost budget exceeded.

**Detection**:
- Track API usage and costs
- Check against budget

**Handling Strategy**:
```python
if current_monthly_cost > BUDGET_LIMIT:
    logger.error("LLM cost budget exceeded")
    return fallback_ranking(restaurants)
```
**Fallback**: Disable LLM, use simple ranking, alert admin
**User Message: "AI recommendations temporarily unavailable."

### 4.7 LLM Context Length Exceeded
**Scenario**: Too many restaurants to send to LLM, exceeding token limit.

**Detection**:
- Estimate token count
- Check against model limit

**Handling Strategy**:
```python
MAX_TOKENS = 4000
if estimate_tokens(restaurant_data) > MAX_TOKENS:
    # Send top N restaurants instead
    restaurant_data = restaurant_data[:20]
```
**Fallback**: Send subset of data, paginate results
**User Message**: None (transparent handling)

### 4.8 LLM Hallucination
**Scenario**: LLM generates false information about restaurants.

**Detection**:
- Validate LLM output against database
- Check for non-existent restaurant IDs

**Handling Strategy**:
```python
# Verify restaurant IDs exist
valid_ids = set(df['id'].tolist())
llm_ids = set([r['id'] for r in llm_recommendations])
invalid_ids = llm_ids - valid_ids
if invalid_ids:
    logger.warning(f"LLM hallucinated restaurants: {invalid_ids}")
    # Remove invalid recommendations
```
**Fallback**: Remove hallucinated entries, use valid ones
**User Message**: None (transparent correction)

## 5. API Edge Cases

### 5.1 Malformed JSON Request
**Scenario**: Client sends invalid JSON in request body.

**Detection**:
- JSON parsing error
- Request validation

**Handling Strategy**:
```python
try:
    data = await request.json()
except json.JSONDecodeError:
    raise HTTPException(status_code=400, detail="Invalid JSON")
```
**Fallback**: Return 400 Bad Request with error details
**User Message**: "Invalid request format. Please check your input."

### 5.2 Missing Required Fields in Request
**Scenario**: Request body missing required fields.

**Detection**:
- Schema validation
- Field presence check

**Handling Strategy**:
```python
required_fields = ['location', 'budget', 'cuisine']
for field in required_fields:
    if field not in data:
        raise HTTPException(status_code=400, detail=f"Missing field: {field}")
```
**Fallback**: Return 400 with missing field list
**User Message**: "Missing required fields: location, budget, cuisine."

### 5.3 Concurrent Requests Overload
**Scenario**: Too many simultaneous requests overwhelm the server.

**Detection**:
- Monitor request queue
- Track active connections

**Handling Strategy**:
```python
# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/recommendations")
@limiter.limit("10/minute")
async def get_recommendations(request: Request):
    ...
```
**Fallback**: Rate limit, queue requests, return 429
**User Message**: "Too many requests. Please try again later."

### 5.4 Large Request Payload
**Scenario**: Client sends extremely large request body.

**Detection**:
- Content-Length header check
- Payload size validation

**Handling Strategy**:
```python
MAX_PAYLOAD_SIZE = 1_000_000  # 1MB
content_length = int(request.headers.get('Content-Length', 0))
if content_length > MAX_PAYLOAD_SIZE:
    raise HTTPException(status_code=413, detail="Payload too large")
```
**Fallback**: Reject request, return 413 Payload Too Large
**User Message**: "Request too large. Please reduce input size."

### 5.5 Unsupported HTTP Method
**Scenario**: Client uses unsupported method (e.g., PUT, DELETE).

**Detection**:
- Route method check
- FastAPI automatic handling

**Handling Strategy**:
```python
@app.post("/api/recommendations")
async def recommendations():
    # Only POST allowed
```
**Fallback**: Return 405 Method Not Allowed
**User Message**: "Method not allowed. Use POST."

### 5.6 Invalid Content-Type
**Scenario**: Client sends wrong content type (e.g., text/plain instead of application/json).

**Detection**:
- Content-Type header validation

**Handling Strategy**:
```python
content_type = request.headers.get('Content-Type', '')
if 'application/json' not in content_type:
    raise HTTPException(status_code=415, detail="Unsupported Media Type")
```
**Fallback**: Return 415 Unsupported Media Type
**User Message**: "Invalid content type. Use application/json."

### 5.7 API Version Mismatch
**Scenario**: Client uses outdated API version.

**Detection**:
- Version header check
- Endpoint versioning

**Handling Strategy**:
```python
api_version = request.headers.get('API-Version', '1.0')
if api_version != CURRENT_API_VERSION:
    raise HTTPException(status_code=400, detail=f"API version {api_version} not supported")
```
**Fallback**: Return 400 with current version info
**User Message**: "API version outdated. Please update your client."

## 6. Frontend Edge Cases

### 6.1 Network Connectivity Loss
**Scenario**: User loses internet connection during request.

**Detection**:
- Network error detection
- Fetch API error handling

**Handling Strategy**:
```javascript
try {
    const response = await fetch('/api/recommendations', options);
} catch (error) {
    if (error.name === 'TypeError') {
        showNetworkError("No internet connection");
    }
}
```
**Fallback**: Show offline message, retry button
**User Message**: "No internet connection. Please check your network."

### 6.2 Slow Network Response
**Scenario**: API takes too long to respond.

**Detection**:
- Timeout handling
- Loading state management

**Handling Strategy**:
```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 30000);

try {
    const response = await fetch(url, { signal: controller.signal });
} catch (error) {
    if (error.name === 'AbortError') {
        showTimeoutError("Request timed out");
    }
}
```
**Fallback**: Show timeout message, retry option
**User Message**: "Request timed out. Please try again."

### 6.3 Browser Incompatibility
**Scenario**: User uses outdated browser without modern features.

**Detection**:
- Feature detection
- Browser version check

**Handling Strategy**:
```javascript
if (!window.fetch || !window.Promise) {
    showBrowserUpgradeMessage("Please upgrade your browser");
}
```
**Fallback**: Show upgrade message, graceful degradation
**User Message**: "Your browser is outdated. Please upgrade for the best experience."

### 6.4 JavaScript Disabled
**Scenario**: User has JavaScript disabled.

**Detection**:
- Noscript tag detection
- Progressive enhancement

**Handling Strategy**:
```html
<noscript>
    <div class="error">
        JavaScript is required for this application.
    </div>
</noscript>
```
**Fallback**: Show message requiring JavaScript
**User Message**: "JavaScript is required. Please enable it in your browser."

### 6.5 Mobile Device Limitations
**Scenario**: User on mobile with limited screen space or performance.

**Detection**:
- User agent detection
- Screen size detection

**Handling Strategy**:
```javascript
if (window.innerWidth < 768) {
    // Use mobile-optimized layout
}
```
**Fallback**: Responsive design, simplified UI
**User Message**: None (transparent handling)

### 6.6 Form Validation Race Condition
**Scenario**: User submits form before validation completes.

**Detection**:
- Disable submit button during validation
- Validation state tracking

**Handling Strategy**:
```javascript
const [isValidating, setIsValidating] = useState(false);
const [canSubmit, setCanSubmit] = useState(false);

handleSubmit = async () => {
    if (!canSubmit) return;
    setIsValidating(true);
    // ... validation and submission
};
```
**Fallback**: Disable submit button, show validation state
**User Message: None (UI feedback)

### 6.7 State Desynchronization
**Scenario**: Frontend state doesn't match backend state after error.

**Detection**:
- Error boundary detection
- State validation

**Handling Strategy**:
```javascript
// Reset state on error
useEffect(() => {
    if (error) {
        resetForm();
    }
}, [error]);
```
**Fallback**: Reset form, show error message
**User Message**: "An error occurred. Please try again."

## 7. Database Edge Cases

### 7.1 Database Connection Failure
**Scenario**: Cannot connect to database server.

**Detection**:
- Connection error handling
- Health check endpoint

**Handling Strategy**:
```python
try:
    conn = psycopg2.connect(DATABASE_URL)
except psycopg2.OperationalError:
    raise DatabaseError("Cannot connect to database")
```
**Fallback**: Use in-memory dataset, show error, alert admin
**User Message**: "Database connection error. Please try again later."

### 7.2 Database Query Timeout
**Scenario**: Query takes too long to execute.

**Detection**:
- Query timeout setting
- Performance monitoring

**Handling Strategy**:
```python
try:
    with connection.cursor() as cursor:
        cursor.execute(query, timeout=10)
except psycopg2.extensions.QueryCanceledError:
    raise DatabaseError("Query timeout")
```
**Fallback**: Use cached data, optimize query, alert admin
**User Message:** "Request taking too long. Please try again."

### 7.3 Deadlock Detection
**Scenario**: Multiple transactions deadlock each other.

**Detection**:
- Deadlock error handling
- Transaction retry logic

**Handling Strategy**:
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        execute_transaction()
        break
    except psycopg2.extensions.TransactionRollbackError:
        if attempt == max_retries - 1:
            raise DatabaseError("Transaction failed after retries")
        time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
```
**Fallback**: Retry transaction, show error if fails
**User Message:** "Transaction failed. Please try again."

### 7.4 Database Schema Mismatch
**Scenario**: Code expects schema that doesn't match database.

**Detection**:
- Schema validation on startup
- Migration checks

**Handling Strategy**:
```python
def validate_schema():
    expected_columns = ['id', 'name', 'location', 'cuisine', 'rating', 'cost_for_two']
    actual_columns = get_table_columns('restaurants')
    if set(expected_columns) != set(actual_columns):
        raise SchemaError("Database schema mismatch")
```
**Fallback**: Run migrations, alert admin
**User Message:** "System maintenance in progress. Please try again later."

### 7.5 Database Full / Disk Space
**Scenario**: Database disk is full, cannot write.

**Detection**:
- Disk space monitoring
- Write error handling

**Handling Strategy**:
```python
try:
    cursor.execute(insert_query)
except psycopg2.OperationalError as e:
    if "disk full" in str(e).lower():
        raise DatabaseError("Disk full")
```
**Fallback**: Alert admin, use read-only mode
**User Message:** "System maintenance in progress."

### 7.6 Connection Pool Exhaustion
**Scenario**: All database connections in use.

**Detection**:
- Connection pool monitoring
- Queue length tracking

**Handling Strategy**:
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)
```
**Fallback**: Queue requests, show busy message
**User Message:** "System busy. Please try again later."

## 8. Cache Edge Cases

### 8.1 Cache Miss
**Scenario**: Requested data not in cache.

**Detection**:
- Cache lookup returns None
- Cache miss rate monitoring

**Handling Strategy**:
```python
cached_data = redis.get(cache_key)
if cached_data is None:
    # Cache miss - fetch from database
    data = fetch_from_database()
    redis.set(cache_key, data, ex=3600)
```
**Fallback**: Fetch from database, populate cache
**User Message:** None (transparent handling)

### 8.2 Cache Stale Data
**Scenario**: Cache has outdated data.

**Detection**:
- TTL expiration
- Version checking

**Handling Strategy**:
```python
# Use short TTL for frequently changing data
redis.set(cache_key, data, ex=300)  # 5 minutes

# Or use cache invalidation
def update_restaurant(restaurant_id):
    update_database(restaurant_id)
    redis.delete(f"restaurant:{restaurant_id}")
```
**Fallback**: Invalidate cache on updates, use reasonable TTL
**User Message:** None (transparent handling)

### 8.3 Cache Server Down
**Scenario**: Redis server unavailable.

**Detection**:
- Connection error handling
- Health checks

**Handling Strategy**:
```python
try:
    cached_data = redis.get(cache_key)
except redis.ConnectionError:
    logger.warning("Cache server down, using database")
    data = fetch_from_database()
```
**Fallback**: Bypass cache, use database directly
**User Message:** None (transparent fallback)

### 8.4 Cache Memory Full
**Scenario**: Redis memory limit reached, eviction triggered.

**Detection**:
- Memory usage monitoring
- Eviction policy configuration

**Handling Strategy**:
```python
# Configure eviction policy
redis.config_set('maxmemory-policy', 'allkeys-lru')

# Monitor memory usage
used_memory = redis.info('used_memory')
max_memory = redis.info('maxmemory')
if used_memory / max_memory > 0.9:
    logger.warning("Cache memory nearly full")
```
**Fallback**: Let Redis evict old data, monitor and alert
**User Message:** None (transparent handling)

### 8.5 Cache Key Collision
**Scenario**: Different data generates same cache key hash.

**Detection**:
- Cache key validation
- Hash collision monitoring

**Handling Strategy**:
```python
# Use unique, descriptive cache keys
cache_key = f"recommendations:{location}:{budget}:{cuisine}:{rating}:{hash(additional_preferences)}"
```
**Fallback**: Use descriptive keys, include all parameters
**User Message:** None (transparent handling)

### 8.6 Cache Poisoning
**Scenario**: Malicious data injected into cache.

**Detection**:
- Input validation before caching
- Cache data integrity checks

**Handling Strategy**:
```python
# Validate data before caching
if not is_valid_response(data):
    raise ValueError("Invalid data for cache")

# Sign cached data
signature = hmac.sign(data)
redis.set(cache_key, {'data': data, 'signature': signature})
```
**Fallback**: Validate cache data on retrieval
**User Message:** None (security measure)

## 9. Cross-Component Edge Cases

### 9.1 Cascading Failures
**Scenario**: Failure in one component causes failures in others.

**Detection**:
- Circuit breaker pattern
- Health check cascading

**Handling Strategy**:
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def call_llm_service():
    # LLM API call
```
**Fallback**: Circuit breaker opens, use fallbacks
**User Message:** "Service temporarily unavailable."

### 9.2 Race Conditions in Concurrent Requests
**Scenario**: Multiple requests modify same data simultaneously.

**Detection**:
- Optimistic locking
- Transaction isolation

**Handling Strategy**:
```python
# Use optimistic locking
current_version = get_version(restaurant_id)
update_with_version(restaurant_id, new_data, current_version)
```
**Fallback**: Retry on conflict, show error if persistent
**User Message:** "Conflict detected. Please try again."

### 9.3 Memory Leaks
**Scenario**: Long-running process consumes increasing memory.

**Detection**:
- Memory profiling
- Resource monitoring

**Handling Strategy**:
```python
# Use context managers
with load_dataset() as dataset:
    process(dataset)

# Clear large objects explicitly
del large_dataframe
gc.collect()
```
**Fallback**: Monitor memory, restart service if needed
**User Message:** None (operational issue)

### 9.4 Timezone Issues
**Scenario**: Timestamps in different timezones cause confusion.

**Detection**:
- Timezone validation
- UTC standardization

**Handling Strategy**:
```python
from datetime import datetime, timezone

# Always store in UTC
timestamp = datetime.now(timezone.utc)

# Convert to user's timezone for display
user_timestamp = timestamp.astimezone(user_timezone)
```
**Fallback:** Standardize on UTC, document timezone handling
**User Message:** None (transparent handling)

## 10. Monitoring and Alerting

### 10.1 Error Rate Thresholds
**Scenario**: Error rate exceeds acceptable threshold.

**Detection**:
- Error rate monitoring
- Alert configuration

**Handling Strategy**:
```python
# Track error rate
if error_rate > 0.05:  # 5% error rate
    send_alert("High error rate detected")
```
**Fallback**: Auto-scale, investigate, alert on-call
**User Message:** None (operational)

### 10.2 Performance Degradation
**Scenario**: Response times increase significantly.

**Detection**:
- Response time monitoring
- Performance alerts

**Handling Strategy**:
```python
if avg_response_time > 2000:  # 2 seconds
    send_alert("Performance degradation detected")
```
**Fallback**: Investigate bottlenecks, optimize queries, scale
**User Message:** None (operational)

### 10.3 Resource Exhaustion
**Scenario**: CPU, memory, or disk usage near limits.

**Detection**:
- Resource monitoring
- Capacity planning

**Handling Strategy**:
```python
cpu_usage = get_cpu_usage()
if cpu_usage > 90:
    send_alert("CPU usage critical")
    trigger_auto_scale()
```
**Fallback**: Auto-scale, alert admin, shed load
**User Message:** None (operational)

## 11. Recovery Strategies

### 11.1 Graceful Degradation
- When LLM fails: Use simple ranking algorithm
- When cache fails: Query database directly
- When database fails: Use in-memory dataset
- When UI fails: Show simplified version

### 11.2 Retry Logic
- Transient failures: Exponential backoff retry
- Permanent failures: Fail fast with clear error
- Rate limits: Respect retry-after headers

### 11.3 Fallback Mechanisms
- Primary LLM → Secondary LLM → Rule-based ranking
- Primary database → Read replica → In-memory cache
- Primary API → Cached responses → Error message

### 11.4 Data Recovery
- Regular database backups
- Dataset versioning
- Cache warming after restart
- Transaction logs for recovery

## 12. Testing Edge Cases

### 12.1 Unit Tests
- Test each edge case in isolation
- Mock external dependencies
- Validate error handling

### 12.2 Integration Tests
- Test component interactions
- Test failure scenarios
- Test recovery mechanisms

### 12.3 Load Tests
- Simulate high concurrent requests
- Test rate limiting
- Test resource exhaustion

### 12.4 Chaos Engineering
- Randomly fail components
- Test system resilience
- Validate graceful degradation

## 13. User Communication Guidelines

### 13.1 Error Messages
- Be specific about what went wrong
- Provide actionable next steps
- Avoid technical jargon
- Maintain consistent tone

### 13.2 Loading States
- Show progress indicators
- Provide estimated time
- Allow cancellation
- Show partial results when available

### 13.3 Success Messages
- Confirm successful operations
- Show result counts
- Provide relevant context
- Offer next actions

### 13.4 Warning Messages
- Highlight potential issues
- Suggest improvements
- Allow user to proceed or adjust
- Don't block unnecessarily

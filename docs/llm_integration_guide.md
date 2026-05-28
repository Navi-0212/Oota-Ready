# LLM Integration Guide

## Overview

This guide explains the LLM integration for the AI-Powered Restaurant Recommendation System using Groq API. The LLM service provides intelligent restaurant recommendations, explanations, and ranking based on user preferences.

## Technology Stack

- **LLM Provider**: Groq
- **Models**: 
  - Primary: LLaMA 3 70B (llama3-70b-8192)
  - Alternative: Mixtral 8x7B, Gemma 7B
- **Python SDK**: groq==0.4.1
- **Retry Logic**: tenacity==8.2.3

## Configuration

### Environment Variables

Configure the following environment variables in `backend/.env`:

```bash
# LLM API Configuration
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
LLM_MODEL=llama3-70b-8192
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# Cache Configuration
CACHE_TTL=86400
CACHE_ENABLED=true
```

### Getting Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

## LLM Service Architecture

### Service Location
`backend/app/services/llm_service.py`

### Key Components

#### 1. LLMService Class
Main service class that handles all LLM interactions.

**Initialization**:
```python
from app.services.llm_service import LLMService

llm_service = LLMService()
```

#### 2. Prompt Engineering

**System Prompt**:
```
You are a restaurant recommendation expert. Your task is to analyze user preferences 
and restaurant data to provide personalized, helpful recommendations.

Consider factors like:
- Cuisine type and quality
- Budget and value for money
- Location convenience
- Rating and reviews
- Additional user preferences (family-friendly, outdoor seating, etc.)
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

Please respond in JSON format with rankings and summary.
```

## API Methods

### generate_recommendations()

Generate LLM-based restaurant recommendations.

**Parameters**:
- `user_preferences` (Dict): User preference dictionary
  - location: Restaurant location
  - budget: Budget category (low/medium/high)
  - cuisine: Cuisine type
  - min_rating: Minimum rating threshold
  - additional_preferences: Additional preferences text
- `restaurants` (List[Dict]): List of restaurant dictionaries

**Returns**:
```python
{
    "rankings": [
        {
            "id": 1,
            "rank": 1,
            "explanation": "This restaurant is perfect for..."
        }
    ],
    "summary": "Based on your preferences..."
}
```

**Example Usage**:
```python
from app.services.llm_service import LLMService

llm_service = LLMService()

user_prefs = {
    'location': 'Delhi',
    'budget': 'medium',
    'cuisine': 'Italian',
    'min_rating': 4.0,
    'additional_preferences': 'family-friendly'
}

restaurants = [...]  # List of restaurant dictionaries

result = llm_service.generate_recommendations(user_prefs, restaurants)
```

### generate_explanation()

Generate explanation for a single restaurant.

**Parameters**:
- `restaurant` (Dict): Restaurant dictionary
- `user_preferences` (Dict): User preference dictionary

**Returns**:
- Explanation text (2-3 sentences)

**Example Usage**:
```python
explanation = llm_service.generate_explanation(
    restaurant={'name': 'Restaurant A', ...},
    user_preferences={'budget': 'medium', ...}
)
```

### rank_with_llm()

Rank restaurants using LLM.

**Parameters**:
- `restaurants` (List[Dict]): List of restaurant dictionaries
- `user_preferences` (Dict): User preference dictionary

**Returns**:
- Ranked list of restaurants with `llm_rank` and `llm_explanation` fields

**Example Usage**:
```python
ranked = llm_service.rank_with_llm(restaurants, user_preferences)
for restaurant in ranked:
    print(f"Rank: {restaurant['llm_rank']}")
    print(f"Explanation: {restaurant['llm_explanation']}")
```

### summarize_recommendations()

Generate summary of top recommendations.

**Parameters**:
- `restaurants` (List[Dict]): List of restaurant dictionaries
- `user_preferences` (Dict): User preference dictionary

**Returns**:
- Summary text

**Example Usage**:
```python
summary = llm_service.summarize_recommendations(restaurants, user_preferences)
print(summary)
```

## Caching Strategy

### Redis Caching

LLM responses are cached in Redis to reduce API calls and costs.

**Cache Key Generation**:
```python
cache_key = f"llm:recommendations:{hash(user_preferences)}:{hash(restaurant_ids)}"
```

**Cache TTL**: 24 hours (configurable via `CACHE_TTL`)

**Cache Management**:
```python
# Clear all LLM cache
llm_service.clear_cache()
```

### Cache Benefits

- Reduces API costs significantly
- Improves response time for repeated queries
- Handles rate limits gracefully
- Provides fallback when API is unavailable

## Error Handling & Fallback

### Retry Logic

The service uses tenacity for automatic retries with exponential backoff:

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def _call_llm(self, prompt: str) -> str:
    # API call logic
```

### Fallback Mechanism

If the LLM API is unavailable or fails, the service falls back to rule-based ranking:

```python
def _fallback_recommendation(self, restaurants):
    # Returns basic rankings without LLM
    # Explanations based on rating and cuisine
```

**Fallback Triggers**:
- API key not configured
- API call fails after retries
- Timeout occurs
- Rate limit exceeded
- Invalid response format

## Response Format

### Expected LLM Response

The LLM is configured to return JSON:

```json
{
  "rankings": [
    {
      "id": 1,
      "rank": 1,
      "explanation": "This restaurant is perfect for your preferences because..."
    }
  ],
  "summary": "Based on your preferences for Italian cuisine in Delhi..."
}
```

### Response Validation

The service validates:
- Response is valid JSON
- Contains 'rankings' field
- Rankings is a list
- Each ranking has required fields (id, rank, explanation)

## Cost Management

### Token Counting

The service tracks token usage through:
- Input tokens: User preferences + restaurant data
- Output tokens: LLM response
- Total tokens: Input + Output

### Cost Optimization

1. **Limit Restaurant Data**: Only send top 10 restaurants to LLM
2. **Caching**: Cache responses to avoid repeated API calls
3. **Model Selection**: Use appropriate model for task
4. **Max Tokens**: Limit output tokens to 1000

### Cost Estimation

Using Groq LLaMA 3 70B:
- Input: ~$0.00059 per 1K tokens
- Output: ~$0.00079 per 1K tokens

Example cost per recommendation:
- Input: ~500 tokens = $0.0003
- Output: ~300 tokens = $0.00024
- **Total**: ~$0.00054 per recommendation

## Testing

### Unit Tests

Run unit tests for LLM service:

```bash
cd backend
pytest tests/test_llm_service.py -v
```

### Test Coverage

The test suite covers:
- Service initialization
- Cache key generation
- Response parsing
- Fallback mechanisms
- Error handling
- Mock API calls

### Integration Testing

Test with actual Groq API:

```python
import os
os.environ['GROQ_API_KEY'] = 'your_actual_key'

from app.services.llm_service import LLMService

llm_service = LLMService()
# Test with real API
```

## Performance Optimization

### Response Time Targets

- Cache hit: < 100ms
- Cache miss (with LLM): < 10s
- Fallback: < 100ms

### Optimization Techniques

1. **Caching**: First optimization for repeated queries
2. **Limit Data**: Send only necessary restaurant fields
3. **Async Calls**: Use async for concurrent requests
4. **Connection Pooling**: Reuse HTTP connections

## Troubleshooting

### Issue: API Key Not Found

**Symptoms**: Warning "GROQ_API_KEY not set in environment variables"

**Solutions**:
1. Check `.env` file exists
2. Verify `GROQ_API_KEY` is set
3. Ensure `.env` is loaded in application

### Issue: API Call Fails

**Symptoms**: Error "Groq API call failed"

**Solutions**:
1. Verify API key is valid
2. Check network connectivity
3. Verify model name is correct
4. Check Groq service status

### Issue: Invalid JSON Response

**Symptoms**: Error "Invalid JSON response"

**Solutions**:
1. Check if model supports JSON output
2. Verify prompt format
3. Adjust temperature parameter
4. Use fallback mechanism

### Issue: Cache Not Working

**Symptoms**: API called repeatedly for same query

**Solutions**:
1. Verify Redis is running
2. Check Redis connection settings
3. Verify cache TTL is set
4. Check cache key generation

### Issue: High API Costs

**Symptoms**: Unexpectedly high LLM costs

**Solutions**:
1. Check cache hit rate
2. Reduce number of restaurants sent to LLM
3. Lower max_tokens parameter
4. Use smaller model for testing

## Best Practices

### 1. Always Use Caching

Enable Redis caching to reduce costs and improve performance.

### 2. Implement Fallback

Always have a fallback mechanism when LLM is unavailable.

### 3. Monitor Usage

Track API usage and costs regularly.

### 4. Optimize Prompts

Keep prompts concise to reduce token usage.

### 5. Test Thoroughly

Test with various user preferences and edge cases.

### 6. Handle Errors Gracefully

Implement proper error handling and user feedback.

### 7. Version Prompts

Keep track of prompt versions for A/B testing.

### 8. Rate Limit Awareness

Be aware of Groq rate limits and implement throttling.

## Security Considerations

### API Key Management

- Never commit API keys to version control
- Use environment variables for API keys
- Rotate API keys regularly
- Use different keys for dev/staging/production

### Input Sanitization

- Validate user input before sending to LLM
- Sanitize restaurant data
- Limit input length to prevent token overflow

### Rate Limiting

- Implement application-level rate limiting
- Monitor API usage
- Set up alerts for unusual activity

## Monitoring

### Key Metrics to Monitor

- API call success rate
- Cache hit rate
- Average response time
- Token usage per request
- Cost per recommendation
- Error rate

### Logging

The service logs:
- API call attempts
- Cache hits/misses
- Errors and exceptions
- Fallback activations

### Alerts

Set up alerts for:
- High error rate (> 5%)
- Low cache hit rate (< 50%)
- High response time (> 10s)
- Unusual cost spikes

## Future Enhancements

### Potential Improvements

1. **Multiple Models**: Support for different models for different tasks
2. **Prompt Versioning**: A/B test different prompts
3. **Streaming Responses**: Implement streaming for faster responses
4. **Fine-tuning**: Fine-tune model on restaurant data
5. **Vector Search**: Add semantic search capabilities
6. **User Personalization**: Learn from user history
7. **Multi-turn Conversations**: Support for follow-up questions

## References

- [Groq Documentation](https://console.groq.com/docs)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [LLaMA 3 Model Card](https://huggingface.co/meta-llama/Meta-Llama-3-70B)
- [Tenacity Documentation](https://github.com/jd/tenacity)

## Support

For issues or questions:
- Check logs for error details
- Review this troubleshooting guide
- Consult Groq documentation
- Open an issue in the project repository

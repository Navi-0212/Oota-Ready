# Testing Guide

This document provides comprehensive information about testing the AI-Powered Restaurant Recommendation System.

## Table of Contents

1. [Backend Testing](#backend-testing)
2. [Frontend Testing](#frontend-testing)
3. [Integration Testing](#integration-testing)
4. [End-to-End Testing](#end-to-end-testing)
5. [Performance Testing](#performance-testing)
6. [Security Testing](#security-testing)
7. [Edge Case Testing](#edge-case-testing)
8. [Test Coverage](#test-coverage)

## Backend Testing

### Running Unit Tests

```bash
cd backend
pytest tests/ -v
```

### Running Tests with Coverage

```bash
cd backend
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

### Running Specific Test Files

```bash
pytest tests/test_data_service.py -v
pytest tests/test_filtering_service.py -v
pytest tests/test_llm_service.py -v
```

### Running Specific Test Classes

```bash
pytest tests/test_data_service.py::TestDataService -v
```

### Running Specific Test Methods

```bash
pytest tests/test_data_service.py::TestDataService::test_get_restaurant_by_id -v
```

### Test Structure

```
backend/tests/
├── conftest.py                 # Shared fixtures
├── test_api_endpoints.py       # API endpoint tests
├── test_data_service.py        # Data service tests
├── test_data_preprocessor.py   # Data preprocessor tests
├── test_db_connection.py       # Database connection tests
├── test_filtering_service.py   # Filtering service tests
├── test_llm_service.py         # LLM service tests
├── test_exceptions.py          # Exception tests
├── test_rate_limiter.py        # Rate limiter tests
├── test_schemas.py             # Pydantic schema tests
├── test_integration.py         # Integration tests
├── test_edge_cases.py          # Edge case tests
├── test_security.py            # Security tests
└── performance/
    └── locustfile.py           # Performance tests
```

## Frontend Testing

### Running Unit Tests

```bash
cd frontend
npm test
```

### Running Tests in Watch Mode

```bash
cd frontend
npm test -- --watch
```

### Running Tests with Coverage

```bash
cd frontend
npm test -- --coverage
```

### Test Structure

```
frontend/src/
├── components/
│   └── __tests__/
│       ├── PreferenceForm.test.tsx
│       ├── RecommendationCard.test.tsx
│       └── ResultsContainer.test.tsx
└── setupTests.ts
```

## Integration Testing

### Running Integration Tests

```bash
cd backend
pytest tests/test_integration.py -v -m integration
```

### Integration Test Scenarios

- Complete recommendation flow with LLM
- Complete recommendation flow without LLM (fallback)
- Get locations then recommendations flow
- Get cuisines then recommendations flow
- Get restaurant by ID then recommendations flow
- Database connection in flow
- Cache hit in data service
- LLM service initialization
- LLM fallback on API failure

## End-to-End Testing

### Installing Playwright

```bash
cd frontend
npx playwright install
```

### Running E2E Tests

```bash
cd frontend
npm run test:e2e
```

### Running E2E Tests in UI Mode

```bash
cd frontend
npm run test:e2e:ui
```

### Running E2E Tests on Specific Browser

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### E2E Test Scenarios

- Load the application
- Display preference form
- Submit form and display recommendations
- Display loading state during submission
- Display error message on API failure
- Filter by different criteria
- Display restaurant details in results
- Handle empty results
- Validate form fields
- Update rating slider
- Add additional preferences
- Responsive design on mobile
- Navigate between different searches

## Performance Testing

### Installing Locust

```bash
cd backend
pip install locust
```

### Running Performance Tests

```bash
cd backend/tests/performance
locust -f locustfile.py --host=http://localhost:8000
```

### Running Performance Tests in Headless Mode

```bash
locust -f locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 1m
```

### Performance Test Parameters

- `-u`: Number of users (concurrent clients)
- `-r`: Spawn rate (users per second)
- `-t`: Run time (e.g., 1m, 5m, 1h)

### Performance Test Scenarios

- Recommendation requests (most common)
- Get locations
- Get cuisines
- Health check
- Rapid recommendations (stress test)

### Performance Targets

- API response time < 2s (p95)
- Frontend load time < 3s
- Database query time < 1s
- Handle 100+ concurrent users

## Security Testing

### Running Security Tests

```bash
cd backend
pytest tests/test_security.py -v
```

### Security Test Scenarios

- SQL injection in location
- SQL injection in cuisine
- SQL injection in preferences
- XSS in location
- XSS in preferences
- XSS in cuisine
- CSRF protection
- Input validation
- Rate limiting
- Authentication (if implemented)
- Data exposure
- Error handling

### Security Best Practices

1. **SQL Injection**: Use parameterized queries (ORM)
2. **XSS**: Sanitize and validate all user inputs
3. **CSRF**: Implement CSRF tokens for state-changing operations
4. **Input Validation**: Validate all inputs on both client and server
5. **Rate Limiting**: Implement rate limiting to prevent abuse
6. **Authentication**: Implement proper authentication if required
7. **Data Exposure**: Never expose sensitive data in responses
8. **Error Handling**: Don't expose internal details in error messages

## Edge Case Testing

### Running Edge Case Tests

```bash
cd backend
pytest tests/test_edge_cases.py -v
```

### Edge Case Scenarios

- Empty dataset
- Missing required fields
- Invalid data types
- Duplicate records
- Dataset download failure
- Corrupted data
- API failures
- Invalid inputs
- Network failures

## Test Coverage

### Generating Coverage Report

```bash
cd backend
pytest --cov=app --cov-report=html
```

### Viewing Coverage Report

Open `backend/htmlcov/index.html` in a browser.

### Coverage Targets

- Overall coverage: 80%+
- Critical services: 90%+
- API endpoints: 85%+

### Improving Coverage

1. Identify uncovered lines in the coverage report
2. Write tests for uncovered code paths
3. Test edge cases and error conditions
4. Test all branches in conditional logic
5. Test exception handling

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Push to any branch
- Pull requests
- Merge to main

### Test Results

Test results are available in the GitHub Actions tab of the repository.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Connection**: Ensure database is running for integration tests
3. **Redis Connection**: Ensure Redis is running for cache tests
4. **LLM API**: Ensure API key is set for LLM tests (or use mocks)
5. **Port Conflicts**: Ensure no other services are using the same ports

### Debugging Tests

Run tests with verbose output:

```bash
pytest -v -s
```

Run tests with pdb debugger:

```bash
pytest --pdb
```

Run specific test with debugging:

```bash
pytest tests/test_file.py::TestClass::test_method --pdb
```

## Best Practices

1. **Write Tests First**: Follow TDD when possible
2. **Keep Tests Independent**: Each test should be independent
3. **Use Descriptive Names**: Test names should describe what they test
4. **Mock External Dependencies**: Mock databases, APIs, etc.
5. **Test Edge Cases**: Don't just test happy paths
6. **Keep Tests Fast**: Unit tests should be fast
7. **Maintain Tests**: Keep tests updated with code changes
8. **Use Fixtures**: Use fixtures for common test data
9. **Test Error Conditions**: Test how code handles errors
10. **Document Tests**: Add comments for complex test logic

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)
- [Locust Documentation](https://docs.locust.io/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

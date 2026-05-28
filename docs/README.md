# AI-Powered Restaurant Recommendation System (Zomato Use Case)

An intelligent restaurant recommendation service that combines structured data with Large Language Models (LLMs) to provide personalized, human-like restaurant suggestions based on user preferences.

## 📋 Overview

This system intelligently suggests restaurants based on user preferences by:
- Taking user preferences (location, budget, cuisine, ratings)
- Using a real-world dataset of restaurants from Zomato
- Leveraging an LLM to generate personalized recommendations
- Displaying clear and useful results with AI-generated explanations

## 🏗️ Architecture

The system follows a microservices-inspired architecture with four main layers:

- **Frontend Layer**: React.js with TypeScript, TailwindCSS, shadcn/ui
- **API Gateway Layer**: FastAPI (Python) for request validation and routing
- **Backend Services Layer**: Data Service, Filtering Service, LLM Service
- **Data Layer**: PostgreSQL, Redis Cache, Hugging Face Datasets

See [architecture.md](./architecture.md) for detailed architecture documentation.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- Git

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd Zomato
```

2. Copy environment file:
```bash
cp backend/.env.example backend/.env
```

3. Update environment variables in `backend/.env`:
- Set your OpenAI API key or Anthropic API key
- Configure database credentials if needed

4. Start all services:
```bash
docker-compose up
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development Setup

#### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate Python virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment file:
```bash
cp .env.example .env
```

5. Update `.env` with your configuration:
- Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- Configure database connection if using external database

6. Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Access the application at http://localhost:3000

## 📁 Project Structure

```
zomato-recommendation/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── db/            # Database models and connections
│   │   ├── models/        # Pydantic models
│   │   ├── services/      # Business logic (data, filtering, LLM)
│   │   ├── utils/         # Utility functions
│   │   └── main.py        # FastAPI application entry point
│   ├── tests/             # Backend tests
│   ├── data/              # Data files
│   ├── requirements.txt   # Python dependencies
│   ├── .env.example       # Environment variables template
│   └── Dockerfile         # Backend Docker configuration
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API service calls
│   │   ├── hooks/         # Custom React hooks
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   ├── Dockerfile         # Frontend Docker configuration
│   └── nginx.conf         # Nginx configuration
├── docker/                # Docker-related files
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── .github/               # GitHub Actions workflows
├── docker-compose.yml     # Docker Compose configuration
├── .gitignore            # Git ignore rules
├── architecture.md       # System architecture documentation
├── edge-case.md          # Edge cases and error handling
├── implementation-plan.md # Phase-wise implementation plan
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `backend/.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_HOST` / `REDIS_PORT`: Redis cache configuration
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: LLM API key
- `LLM_PROVIDER`: Choose between 'openai' or 'anthropic'
- `LLM_MODEL`: Model to use (e.g., 'gpt-4', 'claude-3-opus')
- `CORS_ORIGINS`: Allowed CORS origins

### Database Setup

The system uses PostgreSQL. When using Docker Compose, the database is automatically created with:
- Database name: `zomato`
- User: `zomato_user`
- Password: `zomato_pass`

For production, use a managed PostgreSQL service and update the `DATABASE_URL` accordingly.

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Linting

Backend:
```bash
cd backend
black app/
flake8 app/
mypy app/
```

Frontend:
```bash
cd frontend
npm run lint
```

## 📊 API Endpoints

### POST /api/recommendations
Get personalized restaurant recommendations based on user preferences.

**Request Body:**
```json
{
  "location": "Delhi",
  "budget": "medium",
  "cuisine": "Italian",
  "min_rating": 4.0,
  "additional_preferences": "family-friendly, outdoor seating"
}
```

**Response:**
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
    "summary": "Based on your preferences...",
    "total_results": 10
  }
}
```

### GET /api/locations
Get available restaurant locations.

### GET /api/cuisines
Get available cuisine types.

### GET /health
Health check endpoint.

For full API documentation, visit http://localhost:8000/docs when the backend is running.

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

- **Backend Tests**: Run on every push and pull request
- **Frontend Tests**: Run on every push and pull request
- **Docker Build**: Build Docker images on push to main branch
- **Linting**: Automated code quality checks

See `.github/workflows/ci.yml` for configuration.

## 📈 Implementation Phases

The project is implemented in 8 phases as outlined in [implementation-plan.md](./implementation-plan.md):

1. **Phase 1**: Foundation & Setup ✅
2. **Phase 2**: Data Layer Implementation
3. **Phase 3**: Backend API Development
4. **Phase 4**: LLM Integration
5. **Phase 5**: Frontend Development
6. **Phase 6**: Testing & Quality Assurance
7. **Phase 7**: Deployment & Monitoring
8. **Phase 8**: Optimization & Scaling

## 🚨 Edge Cases & Error Handling

Comprehensive edge case handling is documented in [edge-case.md](./edge-case.md), covering:
- Data-related edge cases
- User input validation
- LLM integration failures
- API error handling
- Database and cache issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is for educational purposes.

## 🙏 Acknowledgments

- Dataset from [Hugging Face](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Inspired by [Zomato](https://www.zomato.com/)
- Built with FastAPI, React, and OpenAI/Anthropic APIs

## 📞 Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Note**: This is Phase 1 of the implementation. The system is currently in the foundation and setup phase. Additional features will be implemented in subsequent phases as outlined in the implementation plan.

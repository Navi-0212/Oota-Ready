# Frontend Development Guide

## Overview

This guide explains the frontend implementation for the AI-Powered Restaurant Recommendation System. The frontend is built with React, TypeScript, TailwindCSS, and uses Zustand for state management.

## Technology Stack

- **Framework**: React 18+ with TypeScript
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **UI Components**: Radix UI primitives
- **Build Tool**: Create React App

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout.tsx          # Main layout wrapper
│   │   ├── Header.tsx          # Header with navigation
│   │   ├── Footer.tsx          # Footer component
│   │   ├── PreferenceForm.tsx  # User preference form
│   │   ├── RecommendationCard.tsx  # Individual restaurant card
│   │   └── ResultsContainer.tsx   # Results display container
│   ├── pages/
│   │   └── HomePage.tsx        # Main application page
│   ├── services/
│   │   └── api.ts             # API service layer
│   ├── store/
│   │   └── index.ts           # Zustand store
│   ├── types/
│   │   └── index.ts           # TypeScript type definitions
│   ├── index.css             # Global styles
│   └── index.tsx             # Application entry point
├── public/                    # Static assets
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript configuration
├── tailwind.config.js        # TailwindCSS configuration
└── Dockerfile                # Docker configuration
```

## Installation

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Setup Steps

1. Navigate to the frontend directory:
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

The application will be available at `http://localhost:3000`

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
REACT_APP_API_URL=http://localhost:8000
```

### API URL Configuration

The API URL is configured in `src/services/api.ts`:
- Default: `http://localhost:8000`
- Can be overridden via `REACT_APP_API_URL` environment variable

## Components

### Layout Components

#### Layout
Main layout wrapper that includes Header and Footer.

**Location**: `src/components/Layout.tsx`

**Props**:
- `children`: React.ReactNode - Child components to render

#### Header
Navigation header with logo and menu items.

**Location**: `src/components/Header.tsx`

**Features**:
- Logo with icon
- Navigation links
- Responsive design

#### Footer
Footer component with copyright information.

**Location**: `src/components/Footer.tsx`

### Form Components

#### PreferenceForm
User preference form for collecting restaurant search criteria.

**Location**: `src/components/PreferenceForm.tsx`

**Features**:
- Location dropdown (with autocomplete)
- Budget selector (low/medium/high)
- Cuisine dropdown (with autocomplete)
- Rating slider (0-5)
- Additional preferences text area
- Form validation
- Submit button with loading state
- Reset functionality

**State Management**:
- Uses Zustand store for preferences
- Fetches locations and cuisines on mount
- Real-time validation feedback

### Display Components

#### RecommendationCard
Individual restaurant recommendation card.

**Location**: `src/components/RecommendationCard.tsx`

**Props**:
- `restaurant`: Restaurant - Restaurant data
- `rank`: number (optional) - Ranking position

**Features**:
- Restaurant name and location
- Cuisine type
- Rating display (star icons)
- Cost for two
- Budget category badge
- Match score indicator
- AI-generated explanation

#### ResultsContainer
Container for displaying recommendation results.

**Location**: `src/components/ResultsContainer.tsx`

**Props**:
- `recommendations`: Restaurant[] - List of restaurants
- `summary`: string - Summary text
- `totalResults`: number - Total number of results
- `isLoading`: boolean - Loading state
- `error`: string | null - Error message

**Features**:
- Loading spinner
- Error display
- Empty state
- Summary section
- Grid layout for cards

### Page Components

#### HomePage
Main application page that integrates all components.

**Location**: `src/pages/HomePage.tsx`

**Features**:
- Preference form
- Results display
- Auto-fetches recommendations when preferences change
- Loading and error states

## State Management

### Zustand Store

**Location**: `src/store/index.ts`

**Store Structure**:
```typescript
interface AppState {
  preferences: RecommendationRequest;
  recommendations: Restaurant[];
  isLoading: boolean;
  error: string | null;
  locations: string[];
  cuisines: string[];
  setPreferences: (preferences: RecommendationRequest) => void;
  setRecommendations: (recommendations: Restaurant[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setLocations: (locations: string[]) => void;
  setCuisines: (cuisines: string[]) => void;
  reset: () => void;
}
```

**Persistence**:
- Preferences are persisted to localStorage
- Uses Zustand persist middleware

## API Integration

### API Service

**Location**: `src/services/api.ts`

**Methods**:

#### getRecommendations
```typescript
getRecommendations(preferences: RecommendationRequest): Promise<RecommendationResponse>
```
Fetches restaurant recommendations based on user preferences.

#### getLocations
```typescript
getLocations(): Promise<LocationResponse>
```
Fetches available restaurant locations.

#### getCuisines
```typescript
getCuisines(): Promise<CuisineResponse>
```
Fetches available cuisine types.

#### getHealth
```typescript
getHealth(): Promise<{ status: string; service: string }>
```
Checks API health status.

**Features**:
- Axios interceptors for request/response
- Error handling
- Timeout configuration (30 seconds)
- Automatic retry on network errors

## Type Definitions

**Location**: `src/types/index.ts`

**Key Types**:

```typescript
interface RecommendationRequest {
  location: string;
  budget: 'low' | 'medium' | 'high';
  cuisine: string;
  min_rating: number;
  additional_preferences: string;
}

interface Restaurant {
  id: number;
  name: string;
  location: string;
  cuisine: string;
  cost_for_two: number;
  rating: number;
  votes?: number;
  reviews?: string;
  address?: string;
  phone?: string;
  url?: string;
  budget_category?: string;
  rating_category?: string;
  match_score?: number;
  explanation?: string;
  llm_rank?: number;
  llm_explanation?: string;
}
```

## Styling

### TailwindCSS Configuration

**Location**: `tailwind.config.js`

**Custom Colors**:
- Primary: Orange (orange-500)
- Secondary: Gray (gray-800)
- Success: Green (green-500)
- Error: Red (red-500)

### Responsive Design

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

**Breakpoints**:
- `grid-cols-1` (mobile)
- `md:grid-cols-2` (tablet)
- `lg:grid-cols-3` (desktop)

## Development

### Running Locally

1. Start backend API:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

2. Start frontend:
```bash
cd frontend
npm start
```

3. Open browser:
```
http://localhost:3000
```

### Building for Production

```bash
npm run build
```

Build artifacts will be in the `build/` directory.

### Linting

```bash
npm run lint
```

### Formatting

```bash
npm run format
```

## Testing

### Running Tests

```bash
npm test
```

### Test Coverage

- Component unit tests
- Integration tests for API calls
- Form validation tests
- Error scenario tests

## Deployment

### Docker Deployment

Build and run with Docker Compose:

```bash
docker-compose up
```

### Manual Deployment

1. Build the frontend:
```bash
npm run build
```

2. Serve the build directory with a web server (e.g., nginx)

## Troubleshooting

### Issue: API Connection Refused

**Symptoms**: Network error when fetching recommendations

**Solutions**:
1. Verify backend API is running on port 8000
2. Check `REACT_APP_API_URL` environment variable
3. Verify CORS configuration on backend

### Issue: Dependencies Not Found

**Symptoms**: Module not found errors

**Solutions**:
1. Run `npm install` to install dependencies
2. Delete `node_modules` and `package-lock.json`, then reinstall
3. Check Node.js version (requires 18+)

### Issue: Styles Not Loading

**Symptoms**: Unstyled components

**Solutions**:
1. Verify TailwindCSS is configured correctly
2. Check that `index.css` is imported
3. Verify TailwindCSS build process

### Issue: State Not Persisting

**Symptoms**: Preferences lost on page refresh

**Solutions**:
1. Check localStorage is enabled in browser
2. Verify Zustand persist middleware is configured
3. Check browser console for errors

## Best Practices

### Component Design

- Keep components small and focused
- Use TypeScript for type safety
- Implement proper error boundaries
- Add loading states for async operations

### State Management

- Use Zustand for global state
- Keep state minimal and focused
- Persist only necessary data
- Use selectors to prevent unnecessary re-renders

### API Integration

- Implement proper error handling
- Add request timeouts
- Use interceptors for common logic
- Implement retry logic for failed requests

### Styling

- Use TailwindCSS utility classes
- Follow responsive-first design
- Use semantic HTML
- Ensure accessibility (ARIA labels, keyboard navigation)

## Performance Optimization

### Code Splitting

Use React.lazy for lazy loading components:
```typescript
const HomePage = React.lazy(() => import('./pages/HomePage'));
```

### Memoization

Use React.memo for expensive components:
```typescript
const RecommendationCard = React.memo<RecommendationCardProps>(({ restaurant, rank }) => {
  // Component implementation
});
```

### Image Optimization

- Use appropriate image formats
- Implement lazy loading for images
- Use responsive images

## Accessibility

### ARIA Labels

Add ARIA labels to interactive elements:
```tsx
<button aria-label="Get recommendations">Submit</button>
```

### Keyboard Navigation

Ensure all interactive elements are keyboard accessible:
- Use semantic HTML
- Add focus indicators
- Implement tab order

### Screen Readers

Provide descriptive text for screen readers:
- Use alt text for images
- Add aria-labels where needed
- Ensure color contrast meets WCAG standards

## Security Considerations

### API Keys

- Never expose API keys in frontend code
- Use environment variables for sensitive data
- Validate all user inputs

### XSS Prevention

- React automatically escapes JSX
- Be cautious with dangerouslySetInnerHTML
- Sanitize user-generated content

### CORS

- Configure CORS on backend
- Use HTTPS in production
- Validate API responses

## Future Enhancements

### Planned Features

1. **User Authentication**
   - Login/signup functionality
   - User preference history
   - Saved searches

2. **Advanced Filtering**
   - More filter options
   - Filter combinations
   - Saved filter presets

3. **Social Features**
   - Share recommendations
   - Rate restaurants
   - Write reviews

4. **Mobile App**
   - React Native implementation
   - Push notifications
   - Offline support

5. **Performance**
   - Service Worker for offline support
   - Image optimization
   - Code splitting

## Support

For issues or questions:
- Check this troubleshooting guide
- Review component documentation
- Check browser console for errors
- Verify backend API is running
- Open an issue in the project repository

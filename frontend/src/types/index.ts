// Type definitions for the frontend

export interface RecommendationRequest {
  location: string;
  budget: 'low' | 'medium' | 'high';
  cuisine: string;
  min_rating: number;
  additional_preferences: string;
}

export interface Restaurant {
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

export interface RecommendationResponse {
  success: boolean;
  data?: {
    recommendations: Restaurant[];
    summary: string;
    total_results: number;
  };
  error?: string;
}

export interface LocationResponse {
  success: boolean;
  data?: string[];
  error?: string;
}

export interface CuisineResponse {
  success: boolean;
  data?: string[];
  error?: string;
}

export interface AppState {
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

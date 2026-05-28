// Zustand store for state management

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AppState, RecommendationRequest, Restaurant } from '../types';

const initialPreferences: RecommendationRequest = {
  location: '',
  budget: 'medium',
  cuisine: '',
  min_rating: 0,
  additional_preferences: '',
};

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      preferences: initialPreferences,
      recommendations: [],
      isLoading: false,
      error: null,
      locations: [],
      cuisines: [],

      setPreferences: (preferences: RecommendationRequest) =>
        set({ preferences }),

      setRecommendations: (recommendations: Restaurant[]) =>
        set({ recommendations }),

      setLoading: (isLoading: boolean) => set({ isLoading }),

      setError: (error: string | null) => set({ error }),

      setLocations: (locations: string[]) => set({ locations }),

      setCuisines: (cuisines: string[]) => set({ cuisines }),

      reset: () =>
        set({
          preferences: initialPreferences,
          recommendations: [],
          isLoading: false,
          error: null,
        }),
    }),
    {
      name: 'zomato-recommendation-store',
      partialize: (state) => ({
        preferences: state.preferences,
      }),
    }
  )
);

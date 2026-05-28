// API service for backend communication

import axios, { AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import {
  RecommendationRequest,
  RecommendationResponse,
  LocationResponse,
  CuisineResponse,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: any) => {
    if (error.code === 'ECONNABORTED') {
      error.message = 'Request timeout. Please try again.';
    } else if (!error.response) {
      error.message = 'Network error. Please check your connection.';
    }
    return Promise.reject(error);
  }
);

export const recommendationApi = {
  getRecommendations: async (
    preferences: RecommendationRequest
  ): Promise<RecommendationResponse> => {
    try {
      const response = await api.post<RecommendationResponse>(
        '/api/recommendations',
        preferences
      );
      return response.data;
    } catch (error) {
      console.error('Error getting recommendations:', error);
      throw error;
    }
  },

  getLocations: async (): Promise<LocationResponse> => {
    try {
      const response = await api.get<LocationResponse>('/api/locations');
      return response.data;
    } catch (error) {
      console.error('Error getting locations:', error);
      throw error;
    }
  },

  getCuisines: async (): Promise<CuisineResponse> => {
    try {
      const response = await api.get<CuisineResponse>('/api/cuisines');
      return response.data;
    } catch (error) {
      console.error('Error getting cuisines:', error);
      throw error;
    }
  },

  getHealth: async (): Promise<{ status: string; service: string }> => {
    try {
      const response = await api.get('/api/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  },
};

export default api;

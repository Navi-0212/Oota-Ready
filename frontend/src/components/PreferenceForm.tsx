// Preference Form component

import React, { useState, useEffect } from 'react';
import { Search, DollarSign, Utensils, Star, MapPin, RefreshCw } from 'lucide-react';
import { RecommendationRequest } from '../types';
import { useStore } from '../store';

const PreferenceForm: React.FC = () => {
  const { preferences, setPreferences, locations, cuisines, setLocations, setCuisines, isLoading } = useStore();
  const [localPreferences, setLocalPreferences] = useState<RecommendationRequest>(preferences);

  useEffect(() => {
    setLocalPreferences(preferences);
  }, [preferences]);

  useEffect(() => {
    // Fetch locations and cuisines on mount
    const fetchMetadata = async () => {
      try {
        const { recommendationApi } = await import('../services/api');
        const [locationsRes, cuisinesRes] = await Promise.all([
          recommendationApi.getLocations(),
          recommendationApi.getCuisines(),
        ]);
        if (locationsRes.success && locationsRes.data && locationsRes.data.length > 0) {
          setLocations(locationsRes.data);
        } else {
          setLocations(["Indiranagar", "Koramangala", "HSR Layout", "Jayanagar", "Whitefield", "MG Road", "Brigade Road", "Electronic City", "BTM Layout", "Frazer Town", "Basavanagudi"]);
        }
        if (cuisinesRes.success && cuisinesRes.data && cuisinesRes.data.length > 0) {
          setCuisines(cuisinesRes.data);
        } else {
          setCuisines(["North Indian", "South Indian", "Chinese", "Italian", "Mexican", "Thai", "Japanese", "Continental", "Biryani", "Kerala", "Andhra", "Mughlai", "Seafood", "Street Food", "Cafe"]);
        }
      } catch (error) {
        console.error('Failed to fetch metadata, using local fallback:', error);
        setLocations(["Indiranagar", "Koramangala", "HSR Layout", "Jayanagar", "Whitefield", "MG Road", "Brigade Road", "Electronic City", "BTM Layout", "Frazer Town", "Basavanagudi"]);
        setCuisines(["North Indian", "South Indian", "Chinese", "Italian", "Mexican", "Thai", "Japanese", "Continental", "Biryani", "Kerala", "Andhra", "Mughlai", "Seafood", "Street Food", "Cafe"]);
      }
    };
    fetchMetadata();
  }, [setLocations, setCuisines]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPreferences(localPreferences);
  };

  const handleReset = () => {
    const resetPrefs: RecommendationRequest = {
      location: '',
      budget: 'medium',
      cuisine: '',
      min_rating: 0,
      additional_preferences: '',
    };
    setLocalPreferences(resetPrefs);
    setPreferences(resetPrefs);
  };

  return (
    <div className="rounded-2xl shadow-2xl p-6 md:p-8" style={{ backgroundColor: '#FFFFFF', boxShadow: '0px 20px 60px rgba(0, 0, 0, 0.15)' }}>
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {/* Location */}
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5" style={{ color: '#8D7168' }} />
            <select
              value={localPreferences.location}
              onChange={(e) => setLocalPreferences({ ...localPreferences, location: e.target.value })}
              className="w-full pl-10 pr-4 py-3 rounded-xl appearance-none focus:outline-none focus:ring-2 transition-all"
              style={{ backgroundColor: '#F8F9FA', border: '1px solid #E0E0E0', fontFamily: 'Inter, sans-serif', color: '#1B1C1C' }}
              required
            >
              <option value="">Location</option>
              {locations.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>

          {/* Budget */}
          <div className="relative">
            <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5" style={{ color: '#8D7168' }} />
            <select
              value={localPreferences.budget}
              onChange={(e) => setLocalPreferences({ ...localPreferences, budget: e.target.value as 'low' | 'medium' | 'high' })}
              className="w-full pl-10 pr-4 py-3 rounded-xl appearance-none focus:outline-none focus:ring-2 transition-all"
              style={{ backgroundColor: '#F8F9FA', border: '1px solid #E0E0E0', fontFamily: 'Inter, sans-serif', color: '#1B1C1C' }}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          {/* Cuisine */}
          <div className="relative">
            <Utensils className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5" style={{ color: '#8D7168' }} />
            <select
              value={localPreferences.cuisine}
              onChange={(e) => setLocalPreferences({ ...localPreferences, cuisine: e.target.value })}
              className="w-full pl-10 pr-4 py-3 rounded-xl appearance-none focus:outline-none focus:ring-2 transition-all"
              style={{ backgroundColor: '#F8F9FA', border: '1px solid #E0E0E0', fontFamily: 'Inter, sans-serif', color: '#1B1C1C' }}
              required
            >
              <option value="">Cuisine</option>
              {cuisines.map((cuisine) => (
                <option key={cuisine} value={cuisine}>
                  {cuisine}
                </option>
              ))}
            </select>
          </div>

          {/* Search Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-6 rounded-xl font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-lg"
            style={{ backgroundColor: '#FF6B35', color: '#FFFFFF', fontFamily: 'Inter, sans-serif' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#E55A2B';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#FF6B35';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <Search className="w-5 h-5" />
            <span>{isLoading ? 'Searching...' : 'Search'}</span>
          </button>
        </div>

        {/* Advanced Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          {/* Rating Slider */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Star className="h-5 w-5" style={{ color: '#FF6B35' }} />
              <span 
                className="text-sm font-medium"
                style={{ color: '#594139', fontFamily: 'Inter, sans-serif' }}
              >
                Min Rating:
              </span>
            </div>
            <div className="flex-1">
              <input
                type="range"
                min="0"
                max="5"
                step="0.5"
                value={localPreferences.min_rating}
                onChange={(e) => setLocalPreferences({ ...localPreferences, min_rating: parseFloat(e.target.value) })}
                className="w-full h-2 rounded-lg appearance-none cursor-pointer"
                style={{ backgroundColor: '#E0E0E0', accentColor: '#FF6B35' }}
              />
            </div>
            <span 
              className="text-sm font-semibold px-3 py-1 rounded-full"
              style={{ 
                backgroundColor: '#FFF5F0', 
                color: '#FF6B35',
                fontFamily: 'Inter, sans-serif'
              }}
            >
              {localPreferences.min_rating}+
            </span>
          </div>

          {/* Reset Button */}
          <button
            type="button"
            onClick={handleReset}
            className="py-3 px-6 rounded-xl font-medium transition-all text-sm flex items-center justify-center space-x-2"
            style={{ backgroundColor: '#F8F9FA', border: '1px solid #E0E0E0', color: '#594139', fontFamily: 'Inter, sans-serif' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#EDEDED';
              e.currentTarget.style.borderColor = '#D0D0D0';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#F8F9FA';
              e.currentTarget.style.borderColor = '#E0E0E0';
            }}
          >
            <RefreshCw className="w-4 h-4" />
            <span>Reset Filters</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default PreferenceForm;

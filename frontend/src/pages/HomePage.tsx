// Home Page component

import React, { useEffect } from 'react';
import { useStore } from '../store';
import PreferenceForm from '../components/PreferenceForm';
import ResultsContainer from '../components/ResultsContainer';
import { recommendationApi } from '../services/api';

const HomePage: React.FC = () => {
  const {
    preferences,
    recommendations,
    isLoading,
    error,
    setRecommendations,
    setLoading,
    setError,
  } = useStore();

  useEffect(() => {
    const fetchRecommendations = async () => {
      // Only fetch if preferences are set
      if (!preferences.location || !preferences.cuisine) {
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await recommendationApi.getRecommendations(preferences);
        
        if (response.success && response.data) {
          setRecommendations(response.data.recommendations);
        } else {
          setError(response.error || 'Failed to get recommendations');
          setRecommendations([]);
        }
      } catch (err: any) {
        setError(err.message || 'An error occurred while fetching recommendations');
        setRecommendations([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [preferences, setLoading, setError, setRecommendations]);

  return (
    <div className="min-h-screen" style={{ fontFamily: 'Inter, sans-serif', backgroundColor: '#FBF9F8' }}>
      {/* Hero Section matching image1 design */}
      <div className="relative overflow-hidden" style={{ minHeight: '500px' }}>
        {/* Background with gradient */}
        <div 
          className="absolute inset-0"
          style={{ 
            background: 'linear-gradient(135deg, #AB3500 0%, #FF6B35 50%, #B7102A 100%)'
          }}
        ></div>
        
        {/* Decorative elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-64 h-64 rounded-full" style={{ backgroundColor: '#FFFFFF' }}></div>
          <div className="absolute bottom-20 right-20 w-96 h-96 rounded-full" style={{ backgroundColor: '#FFFFFF' }}></div>
        </div>
        
        <div className="relative z-10 container mx-auto px-4 py-16 md:py-24">
          <div className="max-w-4xl mx-auto text-center text-white mb-12">
            <h1 
              className="text-5xl md:text-7xl font-bold mb-6"
              style={{ letterSpacing: '-0.03em', lineHeight: '1.1' }}
            >
              Discover Your Next Meal
            </h1>
            <p 
              className="text-xl md:text-2xl opacity-95 font-light"
              style={{ lineHeight: '1.6' }}
            >
              AI-powered restaurant recommendations tailored to your taste
            </p>
          </div>

          {/* Integrated Search/Filter Interface */}
          <div className="max-w-5xl mx-auto">
            <PreferenceForm />
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="container mx-auto px-4 py-12">
        {isLoading || error || recommendations.length > 0 ? (
          <ResultsContainer
            recommendations={recommendations}
            summary={recommendations.length > 0 ? 'Based on your preferences, here are the top recommendations:' : ''}
            isLoading={isLoading}
            error={error}
          />
        ) : null}
      </div>
    </div>
  );
};

export default HomePage;

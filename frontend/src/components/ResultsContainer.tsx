// Results Container component

import React from 'react';
import { AlertCircle, Sparkles } from 'lucide-react';
import { Restaurant } from '../types';
import RecommendationCard from './RecommendationCard';

interface ResultsContainerProps {
  recommendations: Restaurant[];
  summary: string;
  isLoading: boolean;
  error: string | null;
}

const ResultsContainer: React.FC<ResultsContainerProps> = ({
  recommendations,
  summary,
  isLoading,
  error,
}) => {
  if (isLoading) {
    return (
      <div className="rounded-2xl p-8" style={{ backgroundColor: '#FFFFFF', boxShadow: '0px 4px 20px rgba(51, 51, 51, 0.08)' }}>
        <div className="flex items-center justify-center space-x-4">
          <div 
            className="animate-spin rounded-full h-8 w-8 border-b-2"
            style={{ borderColor: '#FF6B35' }}
          ></div>
          <p style={{ color: '#594139', fontFamily: 'Inter, sans-serif' }}>Finding the best restaurants for you...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div 
        className="rounded-lg p-6"
        style={{ backgroundColor: '#FFEBEE', border: '1px solid #FFCDD2' }}
      >
        <div className="flex items-center space-x-3">
          <AlertCircle className="w-6 h-6" style={{ color: '#BA1A1A' }} />
          <div>
            <h3 
              className="font-semibold"
              style={{ color: '#BA1A1A', fontFamily: 'Inter, sans-serif' }}
            >
              Error
            </h3>
            <p 
              className="mt-1"
              style={{ color: '#BA1A1A', fontFamily: 'Inter, sans-serif' }}
            >
              {error}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="rounded-2xl p-8" style={{ backgroundColor: '#FFFFFF', boxShadow: '0px 4px 20px rgba(51, 51, 51, 0.08)' }}>
        <div className="flex flex-col items-center justify-center space-y-4">
          <AlertCircle className="w-12 h-12" style={{ color: '#8D7168' }} />
          <p 
            className="text-center"
            style={{ color: '#594139', fontFamily: 'Inter, sans-serif' }}
          >
            No restaurants found matching your criteria. Try adjusting your preferences.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Summary */}
      {summary && (
        <div 
          className="rounded-2xl p-6"
          style={{ backgroundColor: '#FFFFFF', border: '1px solid #E0E0E0', boxShadow: '0px 4px 20px rgba(51, 51, 51, 0.08)' }}
        >
          <div className="flex items-start space-x-4">
            <div 
              className="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#FFF5F0' }}
            >
              <Sparkles className="w-6 h-6" style={{ color: '#FF6B35' }} />
            </div>
            <div className="flex-1">
              <h3 
                className="font-semibold mb-2"
                style={{ color: '#FF6B35', fontFamily: 'Inter, sans-serif', fontSize: '18px' }}
              >
                AI-Powered Recommendations
              </h3>
              <p 
                className="text-base mb-2"
                style={{ 
                  color: '#1B1C1C', 
                  fontFamily: 'Inter, sans-serif',
                  lineHeight: '1.6'
                }}
              >
                {summary}
              </p>
              <p 
                className="text-sm"
                style={{ 
                  color: '#594139', 
                  fontFamily: 'Inter, sans-serif'
                }}
              >
                Found {recommendations.length} restaurant{recommendations.length !== 1 ? 's' : ''} matching your preferences
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {recommendations.map((restaurant, index) => (
          <div key={restaurant.id} className="relative">
            <RecommendationCard restaurant={restaurant} rank={index + 1} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultsContainer;

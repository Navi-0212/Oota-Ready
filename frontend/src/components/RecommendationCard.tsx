// Recommendation Card component

import React from 'react';
import { Star, MapPin, Utensils, DollarSign, TrendingUp, Sparkles } from 'lucide-react';
import { Restaurant } from '../types';

interface RecommendationCardProps {
  restaurant: Restaurant;
  rank?: number;
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({ restaurant, rank }) => {
  const getBudgetColor = (budget?: string) => {
    switch (budget) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div 
      className="rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-2xl"
      style={{ 
        backgroundColor: '#FFFFFF', 
        boxShadow: rank === 1 ? '0px 12px 40px rgba(255, 107, 53, 0.2)' : '0px 4px 20px rgba(51, 51, 51, 0.08)',
        border: rank === 1 ? '2px solid #FF6B35' : '1px solid #E0E0E0'
      }}
    >
      {rank && (
        <div 
          className="absolute -top-3 -left-3 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold text-sm z-10 shadow-lg"
          style={{ backgroundColor: '#FF6B35' }}
        >
          {rank}
        </div>
      )}
      
      {/* Restaurant Image */}
      <div className="relative h-56" style={{ backgroundColor: '#F8F9FA' }}>
        {restaurant.url ? (
          <img 
            src={restaurant.url} 
            alt={restaurant.name}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.src = '/images/restaurants/placeholder.jpg';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #FFF5F0 0%, #FFE8D6 100%)' }}>
            <Utensils className="w-16 h-16" style={{ color: '#FF6B35' }} />
          </div>
        )}
        
        {/* AI Recommended Badge */}
        <div 
          className="absolute top-4 left-4 px-3 py-1 rounded-full flex items-center space-x-1 shadow-md"
          style={{ 
            background: 'linear-gradient(135deg, #FF6B35 0%, #B7102A 100%)',
            color: '#FFFFFF'
          }}
        >
          <Sparkles className="w-3 h-3" />
          <span className="text-xs font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>AI Recommended</span>
        </div>
        
        {/* Rating Badge */}
        <div 
          className="absolute top-4 right-4 px-3 py-1 rounded-full flex items-center space-x-1 shadow-md"
          style={{ backgroundColor: '#2D6A4F', color: '#FFFFFF' }}
        >
          <Star className="w-4 h-4 fill-current" />
          <span className="text-sm font-semibold">{restaurant.rating}</span>
        </div>
      </div>
      
      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 
              className="text-xl font-bold mb-1"
              style={{ color: '#1B1C1C', fontFamily: 'Inter, sans-serif', fontWeight: '700' }}
            >
              {restaurant.name}
            </h3>
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4" style={{ color: '#8D7168' }} />
              <span className="text-sm" style={{ color: '#594139', fontFamily: 'Inter, sans-serif' }}>
                {restaurant.location}
              </span>
            </div>
          </div>
          {restaurant.match_score && (
            <div 
              className="flex items-center space-x-1 px-3 py-1 rounded-full shadow-sm"
              style={{ 
                backgroundColor: '#FFF5F0',
                color: '#FF6B35',
                border: '1px solid #FFE8D6'
              }}
            >
              <TrendingUp className="w-4 h-4" />
              <span className="text-sm font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
                {Math.round(restaurant.match_score * 100)}% Match
              </span>
            </div>
          )}
        </div>

        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Utensils className="w-4 h-4" style={{ color: '#8D7168' }} />
            <span className="text-sm" style={{ color: '#594139', fontFamily: 'Inter, sans-serif' }}>
              {restaurant.cuisine}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <DollarSign className="w-4 h-4" style={{ color: '#8D7168' }} />
            <span className="text-sm" style={{ color: '#594139', fontFamily: 'Inter, sans-serif' }}>
              ₹{restaurant.cost_for_two} for two
            </span>
            {restaurant.budget_category && (
              <span 
                className="text-xs px-2 py-1 rounded-full font-medium"
                style={{ 
                  backgroundColor: getBudgetColor(restaurant.budget_category).split(' ')[0],
                  color: getBudgetColor(restaurant.budget_category).split(' ')[1],
                  fontFamily: 'Inter, sans-serif'
                }}
              >
                {restaurant.budget_category}
              </span>
            )}
          </div>

          {(restaurant.explanation || restaurant.llm_explanation) && (
            <div 
              className="mt-4 p-4 rounded-xl"
              style={{ backgroundColor: '#FFF5F0', border: '1px solid #FFE8D6' }}
            >
              <p className="text-sm" style={{ color: '#1B1C1C', fontFamily: 'Inter, sans-serif', lineHeight: '1.6' }}>
                <span className="font-semibold" style={{ color: '#FF6B35' }}>Why we recommend this:</span>{' '}
                {restaurant.llm_explanation || restaurant.explanation}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecommendationCard;

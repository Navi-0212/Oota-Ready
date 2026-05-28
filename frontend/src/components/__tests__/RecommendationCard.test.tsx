/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import RecommendationCard from '../RecommendationCard';

describe('RecommendationCard Component', () => {
  const mockRestaurant = {
    id: 1,
    name: 'Test Restaurant',
    location: 'Delhi',
    cuisine: 'Italian',
    cost_for_two: 1000,
    rating: 4.5,
    budget_category: 'medium',
    rating_category: 'very_good',
    match_score: 0.95,
    explanation: 'This restaurant matches your preferences well.'
  };

  test('renders restaurant information', () => {
    render(<RecommendationCard restaurant={mockRestaurant} />);

    expect(screen.getByText('Test Restaurant')).toBeInTheDocument();
    expect(screen.getByText('Delhi')).toBeInTheDocument();
    expect(screen.getByText('Italian')).toBeInTheDocument();
    expect(screen.getByText('₹1000')).toBeInTheDocument();
  });

  test('displays rating with stars', () => {
    render(<RecommendationCard restaurant={mockRestaurant} />);

    expect(screen.getByText(/4\.5/i)).toBeInTheDocument();
    // Check for star icons or rating display
  });

  test('displays match score', () => {
    render(<RecommendationCard restaurant={mockRestaurant} />);

    expect(screen.getByText(/95%/i)).toBeInTheDocument();
  });

  test('displays explanation when provided', () => {
    render(<RecommendationCard restaurant={mockRestaurant} />);

    expect(screen.getByText(/This restaurant matches your preferences well/i)).toBeInTheDocument();
  });

  test('handles missing optional fields', () => {
    const restaurantWithoutOptional = {
      id: 1,
      name: 'Test Restaurant',
      location: 'Delhi',
      cuisine: 'Italian',
      cost_for_two: 1000,
      rating: 4.5
    };

    render(<RecommendationCard restaurant={restaurantWithoutOptional} />);

    expect(screen.getByText('Test Restaurant')).toBeInTheDocument();
    // Should not crash with missing optional fields
  });

  test('displays budget category badge', () => {
    render(<RecommendationCard restaurant={mockRestaurant} />);

    expect(screen.getByText(/medium/i)).toBeInTheDocument();
  });

  test('displays rating category badge', () => {
    render(<RecommendationCard restaurant={mockRestaurant} />);

    expect(screen.getByText(/very good/i)).toBeInTheDocument();
  });
});

/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import ResultsContainer from '../ResultsContainer';

describe('ResultsContainer Component', () => {
  const mockRecommendations = [
    {
      id: 1,
      name: 'Restaurant A',
      location: 'Delhi',
      cuisine: 'Italian',
      cost_for_two: 1000,
      rating: 4.5,
      match_score: 0.95,
      explanation: 'Great match'
    },
    {
      id: 2,
      name: 'Restaurant B',
      location: 'Bangalore',
      cuisine: 'North Indian',
      cost_for_two: 800,
      rating: 4.2,
      match_score: 0.88,
      explanation: 'Good match'
    }
  ];

  test('renders recommendations when provided', () => {
    render(
      <ResultsContainer
        recommendations={mockRecommendations}
        summary="Based on your preferences, we found 2 restaurants."
        totalResults={2}
        isLoading={false}
        error={null}
      />
    );

    expect(screen.getByText('Restaurant A')).toBeInTheDocument();
    expect(screen.getByText('Restaurant B')).toBeInTheDocument();
    expect(screen.getByText(/Based on your preferences/i)).toBeInTheDocument();
    expect(screen.getByText(/2 restaurants/i)).toBeInTheDocument();
  });

  test('displays loading state', () => {
    render(
      <ResultsContainer
        recommendations={[]}
        summary=""
        totalResults={0}
        isLoading={true}
        error={null}
      />
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('displays error message when error is provided', () => {
    render(
      <ResultsContainer
        recommendations={[]}
        summary=""
        totalResults={0}
        isLoading={false}
        error="Failed to fetch recommendations"
      />
    );

    expect(screen.getByText(/Failed to fetch recommendations/i)).toBeInTheDocument();
  });

  test('displays empty state when no recommendations', () => {
    render(
      <ResultsContainer
        recommendations={[]}
        summary="No restaurants found matching your criteria."
        totalResults={0}
        isLoading={false}
        error={null}
      />
    );

    expect(screen.getByText(/No restaurants found/i)).toBeInTheDocument();
  });

  test('displays applied filters when provided', () => {
    render(
      <ResultsContainer
        recommendations={mockRecommendations}
        summary="Found 2 restaurants"
        totalResults={2}
        isLoading={false}
        error={null}
        appliedFilters={{
          location: 'Delhi',
          budget: 'medium',
          cuisine: 'Italian'
        }}
      />
    );

    expect(screen.getByText(/Delhi/i)).toBeInTheDocument();
    expect(screen.getByText(/medium/i)).toBeInTheDocument();
    expect(screen.getByText(/Italian/i)).toBeInTheDocument();
  });
});

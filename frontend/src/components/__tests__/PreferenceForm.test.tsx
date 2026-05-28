/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PreferenceForm from '../PreferenceForm';

describe('PreferenceForm Component', () => {
  const mockOnSubmit = jest.fn();
  const mockLocations = ['Delhi', 'Bangalore', 'Mumbai'];
  const mockCuisines = ['Italian', 'North Indian', 'Chinese'];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders form with all fields', () => {
    render(
      <PreferenceForm
        onSubmit={mockOnSubmit}
        locations={mockLocations}
        cuisines={mockCuisines}
        isLoading={false}
      />
    );

    expect(screen.getByLabelText(/location/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/budget/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/cuisine/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/rating/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/additional preferences/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /get recommendations/i })).toBeInTheDocument();
  });

  test('displays loading state when isLoading is true', () => {
    render(
      <PreferenceForm
        onSubmit={mockOnSubmit}
        locations={mockLocations}
        cuisines={mockCuisines}
        isLoading={true}
      />
    );

    const submitButton = screen.getByRole('button', { name: /loading/i });
    expect(submitButton).toBeDisabled();
  });

  test('submits form with valid data', async () => {
    const user = userEvent.setup();
    
    render(
      <PreferenceForm
        onSubmit={mockOnSubmit}
        locations={mockLocations}
        cuisines={mockCuisines}
        isLoading={false}
      />
    );

    // Fill form
    await user.selectOptions(screen.getByLabelText(/location/i), 'Delhi');
    await user.selectOptions(screen.getByLabelText(/budget/i), 'medium');
    await user.selectOptions(screen.getByLabelText(/cuisine/i), 'Italian');
    
    // Submit form
    await user.click(screen.getByRole('button', { name: /get recommendations/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        location: 'Delhi',
        budget: 'medium',
        cuisine: 'Italian',
        min_rating: 0,
        additional_preferences: ''
      });
    });
  });

  test('updates rating slider value', async () => {
    const user = userEvent.setup();
    
    render(
      <PreferenceForm
        onSubmit={mockOnSubmit}
        locations={mockLocations}
        cuisines={mockCuisines}
        isLoading={false}
      />
    );

    const ratingSlider = screen.getByLabelText(/rating/i);
    await user.clear(ratingSlider);
    await user.type(ratingSlider, '4');

    expect(ratingSlider).toHaveValue(4);
  });

  test('updates additional preferences text area', async () => {
    const user = userEvent.setup();
    
    render(
      <PreferenceForm
        onSubmit={mockOnSubmit}
        locations={mockLocations}
        cuisines={mockCuisines}
        isLoading={false}
      />
    );

    const textArea = screen.getByLabelText(/additional preferences/i);
    await user.type(textArea, 'family-friendly');

    expect(textArea).toHaveValue('family-friendly');
  });

  test('validates required fields', async () => {
    const user = userEvent.setup();
    
    render(
      <PreferenceForm
        onSubmit={mockOnSubmit}
        locations={mockLocations}
        cuisines={mockCuisines}
        isLoading={false}
      />
    );

    // Try to submit without filling required fields
    const submitButton = screen.getByRole('button', { name: /get recommendations/i });
    await user.click(submitButton);

    // Form should not submit if validation fails
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  test('displays all location options', () => {
    render(
      <PreferenceForm
        onSubmit={mockOnSubmit}
        locations={mockLocations}
        cuisines={mockCuisines}
        isLoading={false}
      />
    );

    mockLocations.forEach(location => {
      expect(screen.getByText(location)).toBeInTheDocument();
    });
  });

  test('displays all cuisine options', () => {
    render(
      <PreferenceForm
        onSubmit={mockOnSubmit}
        locations={mockLocations}
        cuisines={mockCuisines}
        isLoading={false}
      />
    );

    mockCuisines.forEach(cuisine => {
      expect(screen.getByText(cuisine)).toBeInTheDocument();
    });
  });

  test('resets form after successful submission', async () => {
    const user = userEvent.setup();
    
    render(
      <PreferenceForm
        onSubmit={mockOnSubmit}
        locations={mockLocations}
        cuisines={mockCuisines}
        isLoading={false}
      />
    );

    // Fill form
    await user.selectOptions(screen.getByLabelText(/location/i), 'Delhi');
    await user.selectOptions(screen.getByLabelText(/budget/i), 'medium');
    await user.type(screen.getByLabelText(/additional preferences/i), 'test');

    // Submit
    await user.click(screen.getByRole('button', { name: /get recommendations/i }));

    // Check if form is reset (this depends on implementation)
    // You may need to add a reset function to the component
  });
});

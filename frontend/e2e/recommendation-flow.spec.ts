import { test, expect } from '@playwright/test';

test.describe('Restaurant Recommendation Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the application', async ({ page }) => {
    await expect(page).toHaveTitle(/Zomato Restaurant Recommendation/);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should display preference form', async ({ page }) => {
    await expect(page.locator('label:has-text("Location")')).toBeVisible();
    await expect(page.locator('label:has-text("Budget")')).toBeVisible();
    await expect(page.locator('label:has-text("Cuisine")')).toBeVisible();
    await expect(page.locator('label:has-text("Rating")')).toBeVisible();
    await expect(page.locator('button:has-text("Get Recommendations")')).toBeVisible();
  });

  test('should submit form and display recommendations', async ({ page }) => {
    // Select location
    await page.selectOption('select[name="location"]', 'Delhi');
    
    // Select budget
    await page.selectOption('select[name="budget"]', 'medium');
    
    // Select cuisine
    await page.selectOption('select[name="cuisine"]', 'Italian');
    
    // Submit form
    await page.click('button:has-text("Get Recommendations")');
    
    // Wait for results
    await expect(page.locator('.results-container')).toBeVisible({ timeout: 10000 });
  });

  test('should display loading state during submission', async ({ page }) => {
    await page.selectOption('select[name="location"]', 'Delhi');
    await page.selectOption('select[name="budget"]', 'medium');
    await page.selectOption('select[name="cuisine"]', 'Italian');
    
    await page.click('button:has-text("Get Recommendations")');
    
    // Check for loading state
    await expect(page.locator('button:has-text("Loading")')).toBeVisible();
  });

  test('should display error message on API failure', async ({ page }) => {
    // Mock API failure by intercepting the request
    await page.route('**/api/recommendations', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ success: false, error: 'Internal Server Error' })
      });
    });

    await page.selectOption('select[name="location"]', 'Delhi');
    await page.selectOption('select[name="budget"]', 'medium');
    await page.selectOption('select[name="cuisine"]', 'Italian');
    
    await page.click('button:has-text("Get Recommendations")');
    
    // Check for error message
    await expect(page.locator('text=Internal Server Error')).toBeVisible({ timeout: 10000 });
  });

  test('should filter by different criteria', async ({ page }) => {
    // First search
    await page.selectOption('select[name="location"]', 'Delhi');
    await page.selectOption('select[name="budget"]', 'low');
    await page.selectOption('select[name="cuisine"]', 'North Indian');
    await page.click('button:has-text("Get Recommendations")');
    
    await expect(page.locator('.results-container')).toBeVisible({ timeout: 10000 });
    
    // Second search with different criteria
    await page.selectOption('select[name="location"]', 'Bangalore');
    await page.selectOption('select[name="budget"]', 'high');
    await page.selectOption('select[name="cuisine"]', 'Chinese');
    await page.click('button:has-text("Get Recommendations")');
    
    await expect(page.locator('.results-container')).toBeVisible({ timeout: 10000 });
  });

  test('should display restaurant details in results', async ({ page }) => {
    await page.selectOption('select[name="location"]', 'Delhi');
    await page.selectOption('select[name="budget"]', 'medium');
    await page.selectOption('select[name="cuisine"]', 'Italian');
    await page.click('button:has-text("Get Recommendations")');
    
    await expect(page.locator('.results-container')).toBeVisible({ timeout: 10000 });
    
    // Check for restaurant card elements
    await expect(page.locator('.recommendation-card').first()).toBeVisible();
  });

  test('should handle empty results', async ({ page }) => {
    // Mock empty response
    await page.route('**/api/recommendations', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ 
          success: false, 
          error: 'No restaurants found matching your criteria' 
        })
      });
    });

    await page.selectOption('select[name="location"]', 'NonExistentCity');
    await page.selectOption('select[name="budget"]', 'medium');
    await page.selectOption('select[name="cuisine"]', 'Italian');
    await page.click('button:has-text("Get Recommendations")');
    
    await expect(page.locator('text=No restaurants found')).toBeVisible({ timeout: 10000 });
  });

  test('should validate form fields', async ({ page }) => {
    // Try to submit without selecting required fields
    await page.click('button:has-text("Get Recommendations")');
    
    // Form should not submit (validation should prevent it)
    await expect(page.locator('.results-container')).not.toBeVisible();
  });

  test('should update rating slider', async ({ page }) => {
    const slider = page.locator('input[type="range"][name="min_rating"]');
    
    await slider.fill('4');
    await expect(slider).toHaveValue('4');
  });

  test('should add additional preferences', async ({ page }) => {
    const textArea = page.locator('textarea[name="additional_preferences"]');
    
    await textArea.fill('family-friendly, outdoor seating');
    await expect(textArea).toHaveValue('family-friendly, outdoor seating');
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await expect(page.locator('label:has-text("Location")')).toBeVisible();
    await expect(page.locator('button:has-text("Get Recommendations")')).toBeVisible();
  });

  test('should navigate between different searches', async ({ page }) => {
    // First search
    await page.selectOption('select[name="location"]', 'Delhi');
    await page.selectOption('select[name="budget"]', 'medium');
    await page.selectOption('select[name="cuisine"]', 'Italian');
    await page.click('button:has-text("Get Recommendations")');
    
    await expect(page.locator('.results-container')).toBeVisible({ timeout: 10000 });
    
    // Clear and search again
    await page.selectOption('select[name="location"]', 'Mumbai');
    await page.click('button:has-text("Get Recommendations")');
    
    await expect(page.locator('.results-container')).toBeVisible({ timeout: 10000 });
  });
});

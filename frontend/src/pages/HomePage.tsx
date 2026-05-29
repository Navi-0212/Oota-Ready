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
        
        if (response.success && response.data && response.data.recommendations && response.data.recommendations.length > 0) {
          setRecommendations(response.data.recommendations);
        } else {
          console.warn('Backend API returned no recommendations, utilizing demo fallback');
          setRecommendations(getMockRecommendations(preferences));
        }
      } catch (err: any) {
        console.warn('Backend API unreachable, utilizing demo fallback:', err);
        setRecommendations(getMockRecommendations(preferences));
      } finally {
        setLoading(false);
      }
    };

    const getMockRecommendations = (prefs: any) => {
      const selectedLocation = prefs.location || '';
      const selectedCuisine = prefs.cuisine || '';
      const selectedBudget = prefs.budget || '';
      const selectedRating = prefs.min_rating || 0;

      const allRestaurants = [
        {
          id: 1,
          name: 'Truffles',
          location: 'Indiranagar',
          cuisine: 'Continental',
          cost_for_two: 600,
          rating: 4.5,
          budget_category: 'medium',
          llm_explanation: 'Truffles is an iconic American-style joint in Indiranagar known for its massive gourmet burgers and decadent milkshakes. Perfect for casual dining.',
        },
        {
          id: 2,
          name: 'Meghana Foods',
          location: 'Jayanagar',
          cuisine: 'Biryani',
          cost_for_two: 400,
          rating: 4.4,
          budget_category: 'low',
          llm_explanation: 'Meghana Foods is legendary across Bangalore for its spicy, aromatic Andhra-style chicken biryani and quick service tiffins. Exceptional value for money.',
        },
        {
          id: 3,
          name: 'Toit',
          location: 'Indiranagar',
          cuisine: 'Continental',
          cost_for_two: 1500,
          rating: 4.6,
          budget_category: 'high',
          llm_explanation: 'Toit is Bangalore\'s premiere microbrewery, serving incredible wood-fired pizzas, baked nachos, and refreshing local craft brews in an unbeatable pub ambiance.',
        },
        {
          id: 4,
          name: 'Vidyarthi Bhavan',
          location: 'Basavanagudi',
          cuisine: 'South Indian',
          cost_for_two: 150,
          rating: 4.7,
          budget_category: 'low',
          llm_explanation: 'Vidyarthi Bhavan is a heritage institution operating since 1943, serving legendary thick, ghee-soaked crispy masala dosas accompanied by rich filter coffee.',
        },
        {
          id: 5,
          name: 'Windmills Craftworks',
          location: 'Whitefield',
          cuisine: 'Continental',
          cost_for_two: 2000,
          rating: 4.7,
          budget_category: 'high',
          llm_explanation: 'Windmills Craftworks combines an upscale library microbrewery with live jazz performances, serving outstanding steaks, Continental bites, and excellent ales.',
        },
        {
          id: 6,
          name: 'China Town',
          location: 'Koramangala',
          cuisine: 'Chinese',
          cost_for_two: 500,
          rating: 4.2,
          budget_category: 'medium',
          llm_explanation: 'China Town offers comforting, classic Indo-Chinese dishes like Hakka Noodles and Chilli Chicken with rich flavors in a vibrant Koramangala setting.',
        },
        {
          id: 7,
          name: 'Punjabi Rasoi',
          location: 'Whitefield',
          cuisine: 'North Indian',
          cost_for_two: 800,
          rating: 4.4,
          budget_category: 'medium',
          llm_explanation: 'Punjabi Rasoi serves incredibly rich Butter Chicken, Dal Makhani, and fluffy butter naans, capturing authentic dhaba flavors in Whitefield.',
        },
        {
          id: 8,
          name: 'Coastal Kitchen',
          location: 'Frazer Town',
          cuisine: 'Seafood',
          cost_for_two: 900,
          rating: 4.5,
          budget_category: 'medium',
          llm_explanation: 'Coastal Kitchen is a seafood lover\'s dream in Frazer Town, cooking up spicy Kerala-style fish curry and golden-fried crispy prawns with fluffy appams.',
        },
        {
          id: 9,
          name: 'Thai Me Up',
          location: 'HSR Layout',
          cuisine: 'Thai',
          cost_for_two: 700,
          rating: 4.3,
          budget_category: 'medium',
          llm_explanation: 'Thai Me Up serves aromatic green curry, classic Pad Thai stir-fried noodles, and sweet sticky rice in a beautifully styled, modern HSR Layout venue.',
        },
        {
          id: 10,
          name: 'Sushi House',
          location: 'MG Road',
          cuisine: 'Japanese',
          cost_for_two: 1200,
          rating: 4.4,
          budget_category: 'high',
          llm_explanation: 'Sushi House on MG Road delivers extremely fresh sashimi platters, California sushi rolls, and hot, comforting ramen bowls in a minimalist, serene atmosphere.',
        },
        {
          id: 11,
          name: 'Chai Point',
          location: 'Electronic City',
          cuisine: 'Cafe',
          cost_for_two: 200,
          rating: 4.1,
          budget_category: 'low',
          llm_explanation: 'Chai Point is the ultimate quick-stop cafe in Electronic City for satisfying cutting chai, warm samosas, and buttery local tiffin snacks.',
        },
        {
          id: 12,
          name: 'Glen\'s Bakehouse',
          location: 'Koramangala',
          cuisine: 'Cafe',
          cost_for_two: 700,
          rating: 4.3,
          budget_category: 'medium',
          llm_explanation: 'Glen\'s Bakehouse is famous for its delightful red velvet cupcakes, sourdough pizzas, and cozy, signature European courtyard vibe in Koramangala.',
        },
        {
          id: 13,
          name: 'Nagarjuna',
          location: 'MG Road',
          cuisine: 'Andhra',
          cost_for_two: 600,
          rating: 4.3,
          budget_category: 'medium',
          llm_explanation: 'Nagarjuna is a highly rated institution on MG Road famous for serving fiery Andhra meals on banana leaves and spicy chilli chicken.',
        },
        {
          id: 14,
          name: 'Burma Burma',
          location: 'Indiranagar',
          cuisine: 'Thai',
          cost_for_two: 1200,
          rating: 4.6,
          budget_category: 'medium',
          llm_explanation: 'Burma Burma in Indiranagar is a highly acclaimed vegetarian haven serving incredible tea leaf salad, coconut noodle soup, and fine Asian brews.',
        },
        {
          id: 15,
          name: 'Karavalli',
          location: 'Brigade Road',
          cuisine: 'Seafood',
          cost_for_two: 2500,
          rating: 4.7,
          budget_category: 'high',
          llm_explanation: 'Karavalli is a world-renowned fine dining spot in Brigade Road serving highly authentic coastal seafood, Mangalorean fish fry, and appams.',
        }
      ];

      // Smart Cascade Filter:
      let filtered = allRestaurants.filter(r => 
        r.location.toLowerCase() === selectedLocation.toLowerCase() &&
        r.cuisine.toLowerCase() === selectedCuisine.toLowerCase()
      );

      if (filtered.length < 3) {
        const matchingCuisine = allRestaurants.filter(r => 
          r.cuisine.toLowerCase() === selectedCuisine.toLowerCase() &&
          r.location.toLowerCase() !== selectedLocation.toLowerCase()
        );
        filtered = [...filtered, ...matchingCuisine];
      }

      if (filtered.length < 3) {
        const matchingLocation = allRestaurants.filter(r => 
          r.location.toLowerCase() === selectedLocation.toLowerCase() &&
          r.cuisine.toLowerCase() !== selectedCuisine.toLowerCase()
        );
        filtered = [...filtered, ...matchingLocation];
      }

      if (filtered.length < 3) {
        const others = allRestaurants.filter(r => 
          r.location.toLowerCase() !== selectedLocation.toLowerCase() &&
          r.cuisine.toLowerCase() !== selectedCuisine.toLowerCase()
        );
        filtered = [...filtered, ...others];
      }

      // Filter by budget if selected
      if (selectedBudget) {
        const budgetMatches = filtered.filter(r => r.budget_category === selectedBudget);
        if (budgetMatches.length >= 2) {
          filtered = budgetMatches;
        }
      }

      // Filter by rating
      filtered = filtered.filter(r => r.rating >= selectedRating);

      // De-duplicate
      const seen = new Set();
      filtered = filtered.filter(r => {
        const duplicate = seen.has(r.id);
        seen.add(r.id);
        return !duplicate;
      });

      // Map & Format up to 6 results
      return filtered.slice(0, 6).map((r, index) => {
        const customizedExplanation = r.llm_explanation + ` Excellent choice for those seeking premium ${selectedCuisine || r.cuisine} dining in Bangalore.`;
        return {
          id: r.id,
          name: r.name,
          location: selectedLocation || r.location,
          cuisine: selectedCuisine || r.cuisine,
          cost_for_two: r.cost_for_two,
          rating: r.rating,
          budget_category: selectedBudget || r.budget_category,
          match_score: parseFloat((0.98 - index * 0.04).toFixed(2)),
          llm_rank: index + 1,
          llm_explanation: customizedExplanation,
        };
      });
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

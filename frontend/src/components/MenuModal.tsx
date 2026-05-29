// Menu Modal component

import React, { useState, useEffect } from 'react';
import { X, Utensils, IndianRupee, Leaf } from 'lucide-react';
import { recommendationApi } from '../services/api';

interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  is_vegetarian: boolean;
  is_available: boolean;
}

interface MenuModalProps {
  restaurantId: number;
  restaurantName: string;
  isOpen: boolean;
  onClose: () => void;
}

const MenuModal: React.FC<MenuModalProps> = ({
  restaurantId,
  restaurantName,
  isOpen,
  onClose,
}) => {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && restaurantId) {
      fetchMenu();
    }
  }, [isOpen, restaurantId]);

  const fetchMenu = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await recommendationApi.getRestaurantMenu(restaurantId);
      if (response.success && response.data) {
        setMenuItems(response.data);
      } else {
        setError(response.message || 'Failed to load menu');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while fetching menu');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  // Group menu items by category
  const groupedItems = menuItems.reduce((acc, item) => {
    const category = item.category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {} as Record<string, MenuItem[]>);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      ></div>

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Utensils className="w-6 h-6" style={{ color: '#FF6B35' }} />
            <h2 className="text-2xl font-bold" style={{ color: '#1B1C1C', fontFamily: 'Inter, sans-serif' }}>
              {restaurantName} Menu
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <X className="w-6 h-6" style={{ color: '#594139' }} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(80vh - 80px)' }}>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: '#FF6B35' }}></div>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-500" style={{ fontFamily: 'Inter, sans-serif' }}>{error}</p>
            </div>
          ) : menuItems.length === 0 ? (
            <div className="text-center py-12">
              <Utensils className="w-16 h-16 mx-auto mb-4" style={{ color: '#E0E0E0' }} />
              <p className="text-gray-500" style={{ fontFamily: 'Inter, sans-serif' }}>No menu items available</p>
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(groupedItems).map(([category, items]) => (
                <div key={category}>
                  <h3 className="text-lg font-semibold mb-3" style={{ color: '#594139', fontFamily: 'Inter, sans-serif' }}>
                    {category}
                  </h3>
                  <div className="space-y-3">
                    {items.map((item) => (
                      <div
                        key={item.id}
                        className="p-4 rounded-xl border border-gray-200 hover:border-orange-300 transition-colors"
                        style={{ backgroundColor: '#FBF9F8' }}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <h4 className="font-semibold" style={{ color: '#1B1C1C', fontFamily: 'Inter, sans-serif' }}>
                                {item.name}
                              </h4>
                              {item.is_vegetarian && (
                                <Leaf className="w-4 h-4" style={{ color: '#22C55E' }} />
                              )}
                            </div>
                            {item.description && (
                              <p className="text-sm text-gray-600 mb-2" style={{ fontFamily: 'Inter, sans-serif' }}>
                                {item.description}
                              </p>
                            )}
                            <div className="flex items-center space-x-2">
                              <IndianRupee className="w-4 h-4" style={{ color: '#FF6B35' }} />
                              <span className="font-semibold" style={{ color: '#FF6B35', fontFamily: 'Inter, sans-serif' }}>
                                {item.price.toFixed(2)}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MenuModal;

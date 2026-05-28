// Header component

import React from 'react';
import { UtensilsCrossed } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header style={{ backgroundColor: '#FFFFFF', borderBottom: '1px solid #E0E0E0', boxShadow: '0px 2px 8px rgba(51, 51, 51, 0.04)' }}>
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <UtensilsCrossed className="h-8 w-8" style={{ color: '#FF6B35' }} />
            <h1 
              className="text-2xl font-bold"
              style={{ 
                color: '#1B1C1C', 
                fontFamily: 'Inter, sans-serif', 
                fontWeight: '700',
                letterSpacing: '-0.02em'
              }}
            >
              Oota Ready
            </h1>
          </div>
          <nav className="flex items-center space-x-6">
            <a
              href="/"
              className="transition-colors"
              style={{ 
                color: '#594139', 
                fontFamily: 'Inter, sans-serif',
                fontWeight: '500'
              }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#FF6B35'}
              onMouseLeave={(e) => e.currentTarget.style.color = '#594139'}
            >
              Home
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;

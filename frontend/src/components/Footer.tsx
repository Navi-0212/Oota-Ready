// Footer component

import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-800 text-white py-6 mt-auto">
      <div className="container mx-auto px-4">
        <div className="text-center">
          <p className="text-gray-400">
            © 2024 Zomato Restaurant Recommendation System
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Powered by AI & Groq
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

"""
Database Models for Restaurant Recommendation System
SQLAlchemy ORM models for restaurant data
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Restaurant(Base):
    """
    Restaurant model
    Represents a restaurant in the database
    """
    __tablename__ = 'restaurants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(100), nullable=False, index=True)
    cuisine = Column(String(100), nullable=False, index=True)
    cost_for_two = Column(Float, nullable=False)
    rating = Column(Float, nullable=False, index=True)
    votes = Column(Integer, default=0)
    reviews = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    url = Column(String(255), nullable=True)
    budget_category = Column(String(20), nullable=True)
    rating_category = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_location_cuisine', 'location', 'cuisine'),
        Index('idx_location_rating', 'location', 'rating'),
        Index('idx_cuisine_rating', 'cuisine', 'rating'),
        Index('idx_budget_rating', 'budget_category', 'rating'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'cuisine': self.cuisine,
            'cost_for_two': self.cost_for_two,
            'rating': self.rating,
            'votes': self.votes,
            'reviews': self.reviews,
            'address': self.address,
            'phone': self.phone,
            'url': self.url,
            'budget_category': self.budget_category,
            'rating_category': self.rating_category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f"<Restaurant(id={self.id}, name='{self.name}', location='{self.location}', cuisine='{self.cuisine}')>"

"""
Database Models for Restaurant Recommendation System
SQLAlchemy ORM models for restaurant data
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Area(Base):
    """
    Area model
    Represents an area/neighborhood in Bangalore
    """
    __tablename__ = 'areas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    city = Column(String(50), nullable=False, default='Bangalore')
    pincode = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'pincode': self.pincode,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<Area(id={self.id}, name='{self.name}', city='{self.city}')>"


class Cuisine(Base):
    """
    Cuisine model
    Represents different cuisine types
    """
    __tablename__ = 'cuisines'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    origin = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'origin': self.origin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<Cuisine(id={self.id}, name='{self.name}')>"


class Restaurant(Base):
    """
    Restaurant model
    Represents a restaurant in the database
    """
    __tablename__ = 'restaurants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=True, index=True)
    location = Column(String(100), nullable=False, index=True)
    cuisine_id = Column(Integer, ForeignKey('cuisines.id'), nullable=True, index=True)
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
    
    # Relationships
    area = relationship("Area", backref="restaurants")
    cuisine_obj = relationship("Cuisine", backref="restaurants")
    menu_items = relationship("MenuItem", backref="restaurant", cascade="all, delete-orphan")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_location_cuisine', 'location', 'cuisine'),
        Index('idx_location_rating', 'location', 'rating'),
        Index('idx_cuisine_rating', 'cuisine', 'rating'),
        Index('idx_budget_rating', 'budget_category', 'rating'),
        Index('idx_area_cuisine', 'area_id', 'cuisine_id'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'area_id': self.area_id,
            'location': self.location,
            'cuisine_id': self.cuisine_id,
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


class MenuItem(Base):
    """
    MenuItem model
    Represents individual menu items with prices
    """
    __tablename__ = 'menu_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=True, index=True)  # e.g., appetizer, main course, dessert
    is_vegetarian = Column(Integer, default=0)  # 0 for non-veg, 1 for veg
    is_available = Column(Integer, default=1)  # 0 for unavailable, 1 for available
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite indexes
    __table_args__ = (
        Index('idx_restaurant_category', 'restaurant_id', 'category'),
        Index('idx_restaurant_price', 'restaurant_id', 'price'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'is_vegetarian': bool(self.is_vegetarian),
            'is_available': bool(self.is_available),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.price}, restaurant_id={self.restaurant_id})>"

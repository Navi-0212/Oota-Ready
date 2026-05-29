"""
Data Ingestion Script for Bangalore Restaurant Data
Populates the database with sample Bangalore restaurant data including areas, cuisines, restaurants, and menu items
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import init_database, get_database
from app.db.models import Area, Cuisine, Restaurant, MenuItem
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ingest_areas(session: Session):
    """Ingest Bangalore areas"""
    areas_data = [
        {"name": "Indiranagar", "city": "Bangalore", "pincode": "560038", "description": "Trendy neighborhood with cafes and pubs"},
        {"name": "Koramangala", "city": "Bangalore", "pincode": "560034", "description": "Popular area with restaurants and tech companies"},
        {"name": "HSR Layout", "city": "Bangalore", "pincode": "560102", "description": "Residential and commercial area"},
        {"name": "Jayanagar", "city": "Bangalore", "pincode": "560041", "description": "Traditional South Bangalore neighborhood"},
        {"name": "Whitefield", "city": "Bangalore", "pincode": "560066", "description": "IT hub with upscale dining"},
        {"name": "MG Road", "city": "Bangalore", "pincode": "560001", "description": "City center with high-end restaurants"},
        {"name": "Brigade Road", "city": "Bangalore", "pincode": "560025", "description": "Shopping and dining district"},
        {"name": "Electronic City", "city": "Bangalore", "pincode": "560100", "description": "Tech park area with food courts"},
        {"name": "BTM Layout", "city": "Bangalore", "pincode": "560076", "description": "Budget-friendly dining area"},
        {"name": "Frazer Town", "city": "Bangalore", "pincode": "560005", "description": "Historic area with diverse cuisine"},
    ]
    
    for area_data in areas_data:
        existing = session.query(Area).filter(Area.name == area_data["name"]).first()
        if not existing:
            area = Area(**area_data)
            session.add(area)
            logger.info(f"Added area: {area_data['name']}")
    
    session.commit()
    logger.info(f"Areas ingestion complete. Total areas: {len(areas_data)}")


def ingest_cuisines(session: Session):
    """Ingest cuisine types"""
    cuisines_data = [
        {"name": "North Indian", "description": "Traditional North Indian cuisine", "origin": "India"},
        {"name": "South Indian", "description": "Traditional South Indian cuisine", "origin": "India"},
        {"name": "Chinese", "description": "Chinese cuisine with Indian adaptations", "origin": "China"},
        {"name": "Italian", "description": "Italian pasta and pizza", "origin": "Italy"},
        {"name": "Mexican", "description": "Mexican tacos and burritos", "origin": "Mexico"},
        {"name": "Thai", "description": "Thai curries and stir-fry", "origin": "Thailand"},
        {"name": "Japanese", "description": "Sushi and ramen", "origin": "Japan"},
        {"name": "Continental", "description": "European-style cuisine", "origin": "Europe"},
        {"name": "Biryani", "description": "Flavored rice dishes", "origin": "India"},
        {"name": "Kerala", "description": "Kerala-style cuisine", "origin": "India"},
        {"name": "Andhra", "description": "Spicy Andhra cuisine", "origin": "India"},
        {"name": "Mughlai", "description": "Mughal-era rich cuisine", "origin": "India"},
        {"name": "Seafood", "description": "Fresh seafood dishes", "origin": "Coastal"},
        {"name": "Street Food", "description": "Indian street food specialties", "origin": "India"},
        {"name": "Cafe", "description": "Coffee shop fare", "origin": "Global"},
    ]
    
    for cuisine_data in cuisines_data:
        existing = session.query(Cuisine).filter(Cuisine.name == cuisine_data["name"]).first()
        if not existing:
            cuisine = Cuisine(**cuisine_data)
            session.add(cuisine)
            logger.info(f"Added cuisine: {cuisine_data['name']}")
    
    session.commit()
    logger.info(f"Cuisines ingestion complete. Total cuisines: {len(cuisines_data)}")


def ingest_restaurants_and_menus(session: Session):
    """Ingest restaurants with menu items"""
    
    # Get areas and cuisines
    areas = {area.name: area for area in session.query(Area).all()}
    cuisines = {cuisine.name: cuisine for cuisine in session.query(Cuisine).all()}
    
    restaurants_data = [
        {
            "name": "Truffles",
            "area": "Indiranagar",
            "cuisine": "Continental",
            "cost_for_two": 600,
            "rating": 4.5,
            "votes": 12500,
            "address": "12th Main, Indiranagar",
            "phone": "+91-80-12345678",
            "budget_category": "medium",
            "rating_category": "excellent",
            "menu_items": [
                {"name": "Classic Burger", "description": "Beef patty with cheese", "price": 250, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Chicken Burger", "description": "Crispy chicken fillet", "price": 220, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Veg Burger", "description": "Paneer patty with veggies", "price": 180, "category": "Main Course", "is_vegetarian": 1},
                {"name": "Loaded Fries", "description": "Cheese and bacon fries", "price": 180, "category": "Appetizer", "is_vegetarian": 0},
                {"name": "Chocolate Shake", "description": "Rich chocolate milkshake", "price": 150, "category": "Beverage", "is_vegetarian": 1},
            ]
        },
        {
            "name": "Meghana Foods",
            "area": "Jayanagar",
            "cuisine": "Biryani",
            "cost_for_two": 400,
            "rating": 4.3,
            "votes": 8900,
            "address": "11th Main, Jayanagar",
            "phone": "+91-80-23456789",
            "budget_category": "low",
            "rating_category": "very_good",
            "menu_items": [
                {"name": "Chicken Biryani", "description": "Andhra-style chicken biryani", "price": 220, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Mutton Biryani", "description": "Spicy mutton biryani", "price": 280, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Veg Biryani", "description": "Mixed vegetable biryani", "price": 180, "category": "Main Course", "is_vegetarian": 1},
                {"name": "Chicken 65", "description": "Spicy fried chicken", "price": 180, "category": "Appetizer", "is_vegetarian": 0},
                {"name": "Raitha", "description": "Curd side dish", "price": 40, "category": "Side Dish", "is_vegetarian": 1},
            ]
        },
        {
            "name": "Toit",
            "area": "Indiranagar",
            "cuisine": "Continental",
            "cost_for_two": 1500,
            "rating": 4.6,
            "votes": 15000,
            "address": "100ft Road, Indiranagar",
            "phone": "+91-80-34567890",
            "budget_category": "high",
            "rating_category": "excellent",
            "menu_items": [
                {"name": "Wood-fired Pizza", "description": "Margherita pizza", "price": 450, "category": "Main Course", "is_vegetarian": 1},
                {"name": "Grilled Chicken", "description": "Herb-marinated chicken", "price": 550, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Fish and Chips", "description": "Beer-battered fish", "price": 480, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Craft Beer", "description": "House-brewed beer", "price": 350, "category": "Beverage", "is_vegetarian": 1},
                {"name": "Caesar Salad", "description": "Classic caesar salad", "price": 280, "category": "Appetizer", "is_vegetarian": 0},
            ]
        },
        {
            "name": "Vidyarthi Bhavan",
            "area": "Basavanagudi",
            "cuisine": "South Indian",
            "cost_for_two": 150,
            "rating": 4.7,
            "votes": 20000,
            "address": "Gandhi Bazaar, Basavanagudi",
            "phone": "+91-80-45678901",
            "budget_category": "low",
            "rating_category": "excellent",
            "menu_items": [
                {"name": "Masala Dosa", "description": "Crispy dosa with potato filling", "price": 50, "category": "Main Course", "is_vegetarian": 1},
                {"name": "Set Dosa", "description": "Soft dosa set", "price": 40, "category": "Main Course", "is_vegetarian": 1},
                {"name": "Idli Vada", "description": "Steamed rice cakes with fritters", "price": 45, "category": "Main Course", "is_vegetarian": 1},
                {"name": "Coffee", "description": "Filter coffee", "price": 20, "category": "Beverage", "is_vegetarian": 1},
                {"name": "Kesari Bath", "description": "Sweet semolina dish", "price": 30, "category": "Dessert", "is_vegetarian": 1},
            ]
        },
        {
            "name": "China Town",
            "area": "Koramangala",
            "cuisine": "Chinese",
            "cost_for_two": 500,
            "rating": 4.2,
            "votes": 7500,
            "address": "5th Block, Koramangala",
            "phone": "+91-80-56789012",
            "budget_category": "medium",
            "rating_category": "very_good",
            "menu_items": [
                {"name": "Chicken Manchurian", "description": "Indo-Chinese chicken balls", "price": 220, "category": "Appetizer", "is_vegetarian": 0},
                {"name": "Hakka Noodles", "description": "Stir-fried noodles", "price": 180, "category": "Main Course", "is_vegetarian": 1},
                {"name": "Chicken Fried Rice", "description": "Egg fried rice with chicken", "price": 200, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Spring Rolls", "description": "Crispy vegetable rolls", "price": 150, "category": "Appetizer", "is_vegetarian": 1},
                {"name": "Hot and Sour Soup", "description": "Spicy tangy soup", "price": 120, "category": "Appetizer", "is_vegetarian": 1},
            ]
        },
        {
            "name": "Punjabi Rasoi",
            "area": "Whitefield",
            "cuisine": "North Indian",
            "cost_for_two": 800,
            "rating": 4.4,
            "votes": 6200,
            "address": "Phoenix Mall, Whitefield",
            "phone": "+91-80-67890123",
            "budget_category": "high",
            "rating_category": "excellent",
            "menu_items": [
                {"name": "Butter Chicken", "description": "Creamy tomato chicken curry", "price": 380, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Paneer Tikka", "description": "Grilled cottage cheese", "price": 280, "category": "Appetizer", "is_vegetarian": 1},
                {"name": "Dal Makhani", "description": "Creamy black lentils", "price": 220, "category": "Main Course", "is_vegetarian": 1},
                {"name": "Naan", "description": "Buttered flatbread", "price": 60, "category": "Bread", "is_vegetarian": 1},
                {"name": "Gulab Jamun", "description": "Sweet milk dumplings", "price": 120, "category": "Dessert", "is_vegetarian": 1},
            ]
        },
        {
            "name": "Coastal Kitchen",
            "area": "Frazer Town",
            "cuisine": "Seafood",
            "cost_for_two": 900,
            "rating": 4.5,
            "votes": 5400,
            "address": "MM Road, Frazer Town",
            "phone": "+91-80-78901234",
            "budget_category": "high",
            "rating_category": "excellent",
            "menu_items": [
                {"name": "Fish Curry", "description": "Kerala-style fish curry", "price": 350, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Prawn Masala", "description": "Spicy prawn dish", "price": 420, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Crab Roast", "description": "Roasted crab with spices", "price": 550, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Appam", "description": "Fermented rice pancake", "price": 80, "category": "Bread", "is_vegetarian": 1},
                {"name": "Fish Fry", "description": "Crispy fried fish", "price": 380, "category": "Main Course", "is_vegetarian": 0},
            ]
        },
        {
            "name": "Thai Me Up",
            "area": "HSR Layout",
            "cuisine": "Thai",
            "cost_for_two": 700,
            "rating": 4.3,
            "votes": 4800,
            "address": "27th Main, HSR Layout",
            "phone": "+91-80-89012345",
            "budget_category": "medium",
            "rating_category": "very_good",
            "menu_items": [
                {"name": "Pad Thai", "description": "Stir-fried rice noodles", "price": 280, "category": "Main Course", "is_vegetarian": 1},
                {"name": "Green Curry", "description": "Thai green curry with chicken", "price": 320, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Tom Yum Soup", "description": "Spicy sour soup", "price": 180, "category": "Appetizer", "is_vegetarian": 0},
                {"name": "Spring Rolls", "description": "Thai-style spring rolls", "price": 160, "category": "Appetizer", "is_vegetarian": 1},
                {"name": "Mango Sticky Rice", "description": "Sweet mango dessert", "price": 200, "category": "Dessert", "is_vegetarian": 1},
            ]
        },
        {
            "name": "Sushi House",
            "area": "MG Road",
            "cuisine": "Japanese",
            "cost_for_two": 1200,
            "rating": 4.4,
            "votes": 3900,
            "address": "Brigade Road, MG Road",
            "phone": "+91-80-90123456",
            "budget_category": "high",
            "rating_category": "excellent",
            "menu_items": [
                {"name": "Salmon Sashimi", "description": "Fresh salmon slices", "price": 450, "category": "Appetizer", "is_vegetarian": 0},
                {"name": "California Roll", "description": "Crab and avocado roll", "price": 380, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Chicken Teriyaki", "description": "Grilled chicken with teriyaki", "price": 420, "category": "Main Course", "is_vegetarian": 0},
                {"name": "Miso Soup", "description": "Traditional soybean soup", "price": 120, "category": "Appetizer", "is_vegetarian": 1},
                {"name": "Vegetable Tempura", "description": "Fried vegetables", "price": 280, "category": "Appetizer", "is_vegetarian": 1},
            ]
        },
        {
            "name": "Chai Point",
            "area": "Electronic City",
            "cuisine": "Cafe",
            "cost_for_two": 200,
            "rating": 4.1,
            "votes": 11000,
            "address": "Tech Park, Electronic City",
            "phone": "+91-80-01234567",
            "budget_category": "low",
            "rating_category": "very_good",
            "menu_items": [
                {"name": "Masala Chai", "description": "Spiced Indian tea", "price": 30, "category": "Beverage", "is_vegetarian": 1},
                {"name": "Ginger Chai", "description": "Ginger-infused tea", "price": 35, "category": "Beverage", "is_vegetarian": 1},
                {"name": "Samosa", "description": "Potato-filled pastry", "price": 25, "category": "Snack", "is_vegetarian": 1},
                {"name": "Vada Pav", "description": "Indian burger", "price": 30, "category": "Snack", "is_vegetarian": 1},
                {"name": "Biscuit", "description": "Assorted biscuits", "price": 20, "category": "Snack", "is_vegetarian": 1},
            ]
        },
    ]
    
    for rest_data in restaurants_data:
        area_name = rest_data["area"]
        cuisine_name = rest_data["cuisine"]
        
        # Handle areas not in our predefined list
        if area_name not in areas:
            new_area = Area(name=area_name, city="Bangalore")
            session.add(new_area)
            session.commit()
            areas[area_name] = new_area
            logger.info(f"Added new area: {area_name}")
        
        # Handle cuisines not in our predefined list
        if cuisine_name not in cuisines:
            new_cuisine = Cuisine(name=cuisine_name)
            session.add(new_cuisine)
            session.commit()
            cuisines[cuisine_name] = new_cuisine
            logger.info(f"Added new cuisine: {cuisine_name}")
        
        # Check if restaurant already exists
        existing = session.query(Restaurant).filter(Restaurant.name == rest_data["name"]).first()
        if not existing:
            restaurant = Restaurant(
                name=rest_data["name"],
                area_id=areas[area_name].id,
                location=area_name,
                cuisine_id=cuisines[cuisine_name].id,
                cuisine=cuisine_name,
                cost_for_two=rest_data["cost_for_two"],
                rating=rest_data["rating"],
                votes=rest_data["votes"],
                address=rest_data.get("address"),
                phone=rest_data.get("phone"),
                budget_category=rest_data.get("budget_category"),
                rating_category=rest_data.get("rating_category"),
            )
            session.add(restaurant)
            session.flush()  # Get the restaurant ID
            
            # Add menu items
            for menu_item_data in rest_data["menu_items"]:
                menu_item = MenuItem(
                    restaurant_id=restaurant.id,
                    name=menu_item_data["name"],
                    description=menu_item_data.get("description"),
                    price=menu_item_data["price"],
                    category=menu_item_data.get("category"),
                    is_vegetarian=menu_item_data["is_vegetarian"],
                    is_available=1,
                )
                session.add(menu_item)
            
            logger.info(f"Added restaurant: {rest_data['name']} with {len(rest_data['menu_items'])} menu items")
    
    session.commit()
    logger.info(f"Restaurants and menu items ingestion complete. Total restaurants: {len(restaurants_data)}")


def main():
    """Main function to run data ingestion"""
    try:
        logger.info("Starting database initialization...")
        db = init_database()
        logger.info("Database initialized successfully")
        
        with db.get_session() as session:
            logger.info("Starting data ingestion...")
            
            # Ingest data in order
            ingest_areas(session)
            ingest_cuisines(session)
            ingest_restaurants_and_menus(session)
            
            logger.info("Data ingestion completed successfully!")
            
            # Print summary
            area_count = session.query(Area).count()
            cuisine_count = session.query(Cuisine).count()
            restaurant_count = session.query(Restaurant).count()
            menu_item_count = session.query(MenuItem).count()
            
            logger.info("\n=== Database Summary ===")
            logger.info(f"Areas: {area_count}")
            logger.info(f"Cuisines: {cuisine_count}")
            logger.info(f"Restaurants: {restaurant_count}")
            logger.info(f"Menu Items: {menu_item_count}")
            logger.info("========================\n")
            
    except Exception as e:
        logger.error(f"Error during data ingestion: {e}")
        raise


if __name__ == "__main__":
    main()

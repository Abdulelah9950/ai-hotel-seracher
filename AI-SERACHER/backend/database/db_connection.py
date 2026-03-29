# MySQL Database Connection
# Handle database connections and queries

import mysql.connector
from mysql.connector import Error
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG


class DatabaseConnection:
    """
    Manages MySQL database connections and provides helper methods for queries
    """
    
    def __init__(self):
        """Initialize database connection"""
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """
        Establish connection to MySQL database
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                db_info = self.connection.get_server_info()
                print(f"[OK] Connected to MySQL Server version {db_info}")
                return True
        except Error as e:
            print(f"[ERROR] Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            print("[OK] MySQL connection closed")
    
    def execute_query(self, query, params=None):
        """
        Execute a SELECT query and return results
        
        Args:
            query (str): SQL SELECT query
            params (tuple): Query parameters for prepared statements
            
        Returns:
            list: List of dictionaries containing query results
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return []
            
            if not self.cursor:
                return []
            
            self.cursor.execute(query, params or ())
            results = self.cursor.fetchall()
            return results
        except Error as e:
            print(f"[ERROR] Query execution error: {e}")
            return []
    
    def execute_update(self, query, params=None):
        """
        Execute an INSERT, UPDATE, or DELETE query
        
        Args:
            query (str): SQL INSERT/UPDATE/DELETE query
            params (tuple): Query parameters for prepared statements
            
        Returns:
            int: Number of affected rows, or -1 if error
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return -1
            
            if not self.cursor:
                return -1
            
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return self.cursor.rowcount
        except Error as e:
            print(f"[ERROR] Update execution error: {e}")
            if self.connection:
                self.connection.rollback()
            return -1
    
    def get_last_insert_id(self):
        """
        Get the ID of the last inserted row
        
        Returns:
            int: Last insert ID
        """
        return self.cursor.lastrowid


# Singleton instance
_db_instance = None

def get_db_connection():
    """
    Get or create database connection singleton
    
    Returns:
        DatabaseConnection: Database connection instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection()
        _db_instance.connect()
    return _db_instance


# Database query helper functions

def get_all_hotels(limit=None):
    """
    Get all hotels from database
    
    Args:
        limit (int): Maximum number of hotels to return
        
    Returns:
        list: List of hotel dictionaries
    """
    db = get_db_connection()
    query = "SELECT * FROM hotels"
    
    if limit:
        query += f" LIMIT {limit}"
    
    return db.execute_query(query)


def get_hotel_by_id(hotel_id):
    """
    Get a specific hotel by ID
    
    Args:
        hotel_id (int): Hotel ID
        
    Returns:
        dict: Hotel data or None if not found
    """
    db = get_db_connection()
    query = "SELECT * FROM hotels WHERE id = %s"
    results = db.execute_query(query, (hotel_id,))
    
    return results[0] if results else None


def get_hotels_by_city(city):
    """
    Get all hotels in a specific city
    
    Args:
        city (str): City name
        
    Returns:
        list: List of hotel dictionaries
    """
    db = get_db_connection()
    query = "SELECT * FROM hotels WHERE city = %s"
    return db.execute_query(query, (city,))


def get_hotels_by_price_range(min_price, max_price):
    """
    Get hotels within a price range
    
    Args:
        min_price (float): Minimum price per night
        max_price (float): Maximum price per night
        
    Returns:
        list: List of hotel dictionaries
    """
    db = get_db_connection()
    query = """
        SELECT * FROM hotels 
        WHERE price_per_night BETWEEN %s AND %s
        ORDER BY price_per_night
    """
    return db.execute_query(query, (min_price, max_price))


def get_hotels_with_amenities(amenities):
    """
    Get hotels that have specific amenities
    
    Args:
        amenities (list): List of amenity names (e.g., ["WiFi", "Pool"])
        
    Returns:
        list: List of hotel dictionaries
    """
    db = get_db_connection()
    
    # Build query to check for each amenity in JSON array
    conditions = []
    params = []
    
    for amenity in amenities:
        conditions.append("JSON_CONTAINS(amenities, %s)")
        params.append(f'"{amenity}"')
    
    query = f"""
        SELECT * FROM hotels 
        WHERE {' AND '.join(conditions)}
    """
    
    return db.execute_query(query, tuple(params))


def get_reviews_by_hotel_id(hotel_id):
    """
    Get all reviews for a specific hotel
    
    Args:
        hotel_id (int): Hotel ID
        
    Returns:
        list: List of review dictionaries
    """
    db = get_db_connection()
    query = """
        SELECT * FROM reviews 
        WHERE hotel_id = %s 
        ORDER BY created_at DESC
    """
    return db.execute_query(query, (hotel_id,))


def get_landmark_by_name(name):
    """
    Get landmark by name (supports fuzzy matching with alternative names)
    
    Args:
        name (str): Landmark name
        
    Returns:
        dict: Landmark data or None if not found
    """
    db = get_db_connection()
    
    # Try exact match first
    query = "SELECT * FROM landmarks WHERE name LIKE %s"
    results = db.execute_query(query, (f"%{name}%",))
    
    if results:
        return results[0]
    
    # Try alternative names
    query = """
        SELECT * FROM landmarks 
        WHERE JSON_SEARCH(alternative_names, 'one', %s) IS NOT NULL
    """
    results = db.execute_query(query, (f"%{name}%",))
    
    return results[0] if results else None


def get_all_landmarks():
    """
    Get all landmarks
    
    Returns:
        list: List of landmark dictionaries
    """
    db = get_db_connection()
    query = "SELECT * FROM landmarks"
    return db.execute_query(query)


def search_hotels(filters):
    """
    Search hotels with multiple filters
    
    Args:
        filters (dict): Dictionary containing search filters
            - city (str): City name
            - min_price (float): Minimum price
            - max_price (float): Maximum price
            - min_rating (float): Minimum star rating
            - amenities (list): Required amenities
            
    Returns:
        list: List of hotel dictionaries
    """
    db = get_db_connection()
    
    conditions = []
    params = []
    
    # City filter
    if filters.get('city'):
        conditions.append("city = %s")
        params.append(filters['city'])
    
    # Price range filter
    if filters.get('min_price') is not None:
        conditions.append("price_per_night >= %s")
        params.append(filters['min_price'])
    
    if filters.get('max_price') is not None:
        conditions.append("price_per_night <= %s")
        params.append(filters['max_price'])
    
    # Rating filter
    if filters.get('min_rating'):
        conditions.append("star_rating >= %s")
        params.append(filters['min_rating'])
    
    # Amenities filter
    if filters.get('amenities'):
        for amenity in filters['amenities']:
            conditions.append("JSON_CONTAINS(amenities, %s)")
            params.append(f'"{amenity}"')
    
    # Build query
    query = "SELECT * FROM hotels"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY star_rating DESC, price_per_night ASC"
    
    # Limit results
    limit = filters.get('limit', 20)
    query += f" LIMIT {limit}"
    
    return db.execute_query(query, tuple(params))


# Test function
def test_connection():
    """
    Test database connection and basic queries
    """
    print("\n" + "=" * 50)
    print("Testing Database Connection")
    print("=" * 50)
    
    db = get_db_connection()
    
    # Test 1: Get hotel count
    hotels = get_all_hotels()
    print(f"\n[OK] Total hotels in database: {len(hotels)}")
    
    # Test 2: Get hotels by city
    makkah_hotels = get_hotels_by_city('Makkah')
    print(f"[OK] Hotels in Makkah: {len(makkah_hotels)}")
    
    # Test 3: Get sample hotel
    if hotels:
        sample = hotels[0]
        print(f"[OK] Sample hotel: {sample['name']} ({sample['price_per_night']} SAR)")
    
    # Test 4: Get landmarks
    landmarks = get_all_landmarks()
    print(f"[OK] Total landmarks: {len(landmarks)}")
    
    print("\n" + "=" * 50)
    print("Database connection is working perfectly!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    # Run test when script is executed directly
    test_connection()

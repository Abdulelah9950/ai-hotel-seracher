# Fetch Hotels from Google Maps Places API
# This script fetches hotel data from Google Maps and stores it in the database

import requests
import json
import time
from decimal import Decimal

# You'll need to install these packages:
# pip install requests mysql-connector-python

"""
GOOGLE MAPS PLACES API SETUP GUIDE
===================================

1. Get API Key:
   - Go to: https://console.cloud.google.com/
   - Create a new project or select existing one
   - Enable these APIs:
     * Places API
     * Geocoding API
     * Maps JavaScript API
   - Go to "Credentials" and create an API key
   - Copy your API key and paste it below

2. API Pricing (Important):
   - Google gives $200 free credit per month
   - Places API costs: $0.017 per request
   - With free credit, you can make ~11,000 requests/month
   - Each nearby search returns up to 60 results (20 per page)

3. Recommended Approach:
   - Fetch hotels once and store in database
   - Update periodically (weekly/monthly) instead of real-time
   - This saves API costs and improves performance
"""

# ===================================
# CONFIGURATION
# ===================================

# Replace with your actual Google Maps API key
GOOGLE_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY_HERE"

# Database configuration (update with your MySQL credentials)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'hotel_booking_ai'
}

# Cities to search for hotels
CITIES = [
    {
        'name': 'Makkah',
        'lat': 21.4225,
        'lng': 39.8262,
        'radius': 10000  # 10km radius
    },
    {
        'name': 'Madinah',
        'lat': 24.4672,
        'lng': 39.6108,
        'radius': 10000
    },
    {
        'name': 'Riyadh',
        'lat': 24.7136,
        'lng': 46.6753,
        'radius': 15000  # 15km radius (larger city)
    },
    {
        'name': 'Jeddah',
        'lat': 21.5433,
        'lng': 39.1728,
        'radius': 15000
    }
]

# ===================================
# GOOGLE PLACES API FUNCTIONS
# ===================================

def search_hotels_nearby(latitude, longitude, radius=5000, api_key=GOOGLE_API_KEY):
    """
    Search for hotels near a specific location using Google Places API
    
    Args:
        latitude: Center point latitude
        longitude: Center point longitude
        radius: Search radius in meters (max 50000)
        api_key: Your Google Maps API key
        
    Returns:
        List of hotel data dictionaries
    """
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    all_hotels = []
    next_page_token = None
    
    # Google Places API returns max 20 results per request
    # Use pagetoken to get up to 60 results total (3 pages)
    
    while True:
        params = {
            'location': f"{latitude},{longitude}",
            'radius': radius,
            'type': 'lodging',  # This includes hotels, motels, etc.
            'key': api_key
        }
        
        if next_page_token:
            params['pagetoken'] = next_page_token
            # Google requires a short delay before requesting next page
            time.sleep(2)
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                hotels = data.get('results', [])
                all_hotels.extend(hotels)
                print(f"Fetched {len(hotels)} hotels (Total: {len(all_hotels)})")
                
                # Check if there's a next page
                next_page_token = data.get('next_page_token')
                if not next_page_token:
                    break
            else:
                print(f"API Error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break
    
    return all_hotels


def get_place_details(place_id, api_key=GOOGLE_API_KEY):
    """
    Get detailed information about a specific place
    
    Args:
        place_id: Google Place ID
        api_key: Your Google Maps API key
        
    Returns:
        Dictionary with detailed place information
    """
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,geometry,rating,price_level,photos,reviews,formatted_phone_number,website',
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'OK':
            return data.get('result', {})
        else:
            print(f"Details API Error: {data.get('status')}")
            return {}
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}


# ===================================
# DATA PROCESSING FUNCTIONS
# ===================================

def extract_amenities_from_types(place_types):
    """
    Extract common hotel amenities from Google place types
    This is a simplified mapping - you can expand it
    """
    amenities = ["WiFi"]  # Assume WiFi is standard
    
    amenity_mapping = {
        'swimming_pool': 'Pool',
        'parking': 'Parking',
        'gym': 'Gym',
        'spa': 'Spa',
        'restaurant': 'Restaurant'
    }
    
    for place_type in place_types:
        if place_type in amenity_mapping:
            amenities.append(amenity_mapping[place_type])
    
    return list(set(amenities))  # Remove duplicates


def estimate_price_from_level(price_level):
    """
    Convert Google's price_level (0-4) to estimated price in SAR
    
    Google's price levels:
    0 = Free
    1 = Inexpensive
    2 = Moderate
    3 = Expensive
    4 = Very Expensive
    """
    
    price_mapping = {
        0: 150,   # Free/Very cheap
        1: 250,   # Inexpensive
        2: 450,   # Moderate
        3: 750,   # Expensive
        4: 1200   # Very Expensive
    }
    
    return price_mapping.get(price_level, 400)  # Default to moderate


def parse_hotel_data(hotel_raw, city_name):
    """
    Parse raw Google Places API data into our database format
    
    Args:
        hotel_raw: Raw hotel data from Google API
        city_name: Name of the city
        
    Returns:
        Dictionary formatted for database insertion
    """
    
    # Extract basic information
    name = hotel_raw.get('name', 'Unknown Hotel')
    address = hotel_raw.get('vicinity', '') or hotel_raw.get('formatted_address', '')
    
    # Get coordinates
    location = hotel_raw.get('geometry', {}).get('location', {})
    latitude = location.get('lat', 0.0)
    longitude = location.get('lng', 0.0)
    
    # Get rating (Google uses 0-5 scale, same as star rating)
    star_rating = hotel_raw.get('rating', 3.5)
    
    # Get price level and convert to SAR
    price_level = hotel_raw.get('price_level')
    price_per_night = estimate_price_from_level(price_level) if price_level is not None else 400
    
    # Extract amenities from types
    place_types = hotel_raw.get('types', [])
    amenities = extract_amenities_from_types(place_types)
    
    # Get Google Place ID
    google_place_id = hotel_raw.get('place_id', '')
    
    # Create description
    description = f"Hotel in {city_name}"
    if hotel_raw.get('rating'):
        total_ratings = hotel_raw.get('user_ratings_total', 0)
        description += f" with {star_rating} rating from {total_ratings} reviews"
    
    return {
        'name': name,
        'address': address,
        'city': city_name,
        'country': 'Saudi Arabia',
        'latitude': latitude,
        'longitude': longitude,
        'description': description,
        'star_rating': star_rating,
        'amenities': json.dumps(amenities),  # Convert to JSON string
        'price_per_night': price_per_night,
        'google_place_id': google_place_id
    }


# ===================================
# DATABASE FUNCTIONS
# ===================================

def insert_hotel_to_db(hotel_data, db_connection):
    """
    Insert hotel data into MySQL database
    
    Args:
        hotel_data: Dictionary with hotel information
        db_connection: MySQL database connection
        
    Returns:
        Hotel ID if successful, None otherwise
    """
    
    cursor = db_connection.cursor()
    
    # Check if hotel already exists (by Google Place ID)
    check_query = "SELECT id FROM hotels WHERE google_place_id = %s"
    cursor.execute(check_query, (hotel_data['google_place_id'],))
    existing = cursor.fetchone()
    
    if existing:
        print(f"Hotel '{hotel_data['name']}' already exists in database (ID: {existing[0]})")
        return existing[0]
    
    # Insert new hotel
    insert_query = """
        INSERT INTO hotels 
        (name, address, city, country, latitude, longitude, description, 
         star_rating, amenities, price_per_night, google_place_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (
        hotel_data['name'],
        hotel_data['address'],
        hotel_data['city'],
        hotel_data['country'],
        hotel_data['latitude'],
        hotel_data['longitude'],
        hotel_data['description'],
        hotel_data['star_rating'],
        hotel_data['amenities'],
        hotel_data['price_per_night'],
        hotel_data['google_place_id']
    )
    
    try:
        cursor.execute(insert_query, values)
        db_connection.commit()
        hotel_id = cursor.lastrowid
        print(f"✓ Inserted: {hotel_data['name']} (ID: {hotel_id})")
        return hotel_id
    except Exception as e:
        print(f"✗ Error inserting {hotel_data['name']}: {e}")
        db_connection.rollback()
        return None
    finally:
        cursor.close()


# ===================================
# MAIN FUNCTION
# ===================================

def fetch_and_store_hotels():
    """
    Main function to fetch hotels from Google Maps and store in database
    """
    
    # Check if API key is set
    if GOOGLE_API_KEY == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        print("ERROR: Please set your Google Maps API key in the GOOGLE_API_KEY variable")
        print("Get your API key from: https://console.cloud.google.com/")
        return
    
    # Import MySQL connector
    try:
        import mysql.connector
    except ImportError:
        print("ERROR: mysql-connector-python not installed")
        print("Run: pip install mysql-connector-python")
        return
    
    # Connect to database
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        print("✓ Connected to database")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("Make sure MySQL is running and credentials are correct")
        return
    
    total_inserted = 0
    total_existing = 0
    
    # Fetch hotels for each city
    for city in CITIES:
        print(f"\n{'='*50}")
        print(f"Searching for hotels in {city['name']}")
        print(f"{'='*50}")
        
        # Search for hotels
        hotels_raw = search_hotels_nearby(
            city['lat'], 
            city['lng'], 
            city['radius']
        )
        
        print(f"Found {len(hotels_raw)} hotels in {city['name']}")
        
        # Process and store each hotel
        for hotel_raw in hotels_raw:
            hotel_data = parse_hotel_data(hotel_raw, city['name'])
            hotel_id = insert_hotel_to_db(hotel_data, db)
            
            if hotel_id:
                if hotel_id > 0:
                    total_inserted += 1
                else:
                    total_existing += 1
            
            # Small delay to respect API rate limits
            time.sleep(0.1)
    
    # Close database connection
    db.close()
    
    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"✓ New hotels inserted: {total_inserted}")
    print(f"• Hotels already in database: {total_existing}")
    print(f"Total hotels: {total_inserted + total_existing}")


# ===================================
# ALTERNATIVE: FETCH DETAILED INFO
# ===================================

def fetch_hotel_reviews_from_google(place_id):
    """
    Get reviews for a specific hotel from Google Places
    This can be used to populate the reviews table
    
    Note: This costs additional API credits
    """
    
    details = get_place_details(place_id)
    reviews = details.get('reviews', [])
    
    processed_reviews = []
    for review in reviews:
        processed_reviews.append({
            'guest_name': review.get('author_name', 'Anonymous'),
            'rating': review.get('rating', 3),
            'review_text': review.get('text', ''),
            'sentiment_score': 0.0  # Will be calculated by sentiment_analyzer.py
        })
    
    return processed_reviews


# ===================================
# RUN SCRIPT
# ===================================

if __name__ == "__main__":
    print("="*50)
    print("GOOGLE MAPS HOTEL FETCHER")
    print("="*50)
    print("\nThis script will fetch hotels from Google Maps Places API")
    print("and store them in your MySQL database.\n")
    
    # Check if user wants to proceed
    response = input("Do you want to continue? (yes/no): ").lower()
    
    if response in ['yes', 'y']:
        fetch_and_store_hotels()
    else:
        print("Operation cancelled.")

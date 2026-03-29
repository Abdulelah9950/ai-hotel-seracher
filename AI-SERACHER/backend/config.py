# Configuration settings
# Store database credentials, API keys, and other settings here

import os
from dotenv import load_dotenv

# Load environment variables from .env file (optional)
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Modtha@7'),
    'database': os.getenv('DB_NAME', 'hotel_booking_ai'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')

# Geoapify API Configuration (Free alternative to Google Places)
# Free tier: 3000 requests/day, no credit card required
# Sign up at: https://www.geoapify.com/
GEOAPIFY_API_KEY = os.getenv('GEOAPIFY_API_KEY', '')

# Flask Configuration
FLASK_CONFIG = {
    'DEBUG': False,  # Disabled for testing - debug mode causes reloader issues
    'HOST': '127.0.0.1',  # Explicit IPv4 address
    'PORT': 5000
}

# AI Configuration
AI_CONFIG = {
    # Fuzzy matching threshold (0-100, higher = more strict)
    'FUZZY_MATCH_THRESHOLD': 70,
    
    # Price ranges in SAR (used as universal baseline for all countries)
    # Note: Prices are estimated based on star ratings, not actual rates
    'PRICE_RANGES': {
        'low': (0, 400),
        'medium': (400, 800),
        'high': (800, 10000)
    },
    
    # Default search radius in kilometers
    'DEFAULT_SEARCH_RADIUS': 5,
    
    # Maximum number of hotels to return
    'MAX_RESULTS': 20
}

# API Routes
# Define all REST API endpoints here

from flask import Blueprint, request, jsonify
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import (
    get_all_hotels, get_hotel_by_id, get_hotels_by_city,
    get_reviews_by_hotel_id, search_hotels, get_landmark_by_name
)
from database.models import Hotel, Review
from ai_modules.query_parser import QueryParser
from ai_modules.sentiment_analyzer import SentimentAnalyzer
from ai_modules.location_matcher import LocationMatcher
from ai_modules.recommendation import RecommendationEngine
from utils.distance_calculator import DistanceCalculator
from services.geoapify_service import GeoapifyService

# Hardcoded major Saudi landmarks (coordinates for Geoapify searches)
# These don't require database access
LANDMARKS = {
    'al-haram': {'name': 'Al-Haram (Kaaba)', 'city': 'Makkah', 'latitude': 21.4225, 'longitude': 39.8262},
    'haram': {'name': 'Al-Haram (Kaaba)', 'city': 'Makkah', 'latitude': 21.4225, 'longitude': 39.8262},
    'kaaba': {'name': 'Kaaba', 'city': 'Makkah', 'latitude': 21.4225, 'longitude': 39.8262},
    'prophet\'s mosque': {'name': 'Prophet\'s Mosque', 'city': 'Madinah', 'latitude': 24.4703, 'longitude': 39.6068},
    'prophets mosque': {'name': 'Prophet\'s Mosque', 'city': 'Madinah', 'latitude': 24.4703, 'longitude': 39.6068},
    'prophet mosque': {'name': 'Prophet\'s Mosque', 'city': 'Madinah', 'latitude': 24.4703, 'longitude': 39.6068},
    'masjid nabawi': {'name': 'Prophet\'s Mosque', 'city': 'Madinah', 'latitude': 24.4703, 'longitude': 39.6068},
    'masjid al-nabawi': {'name': 'Prophet\'s Mosque', 'city': 'Madinah', 'latitude': 24.4703, 'longitude': 39.6068},
    'al-masjid an-nabawi': {'name': 'Prophet\'s Mosque', 'city': 'Madinah', 'latitude': 24.4703, 'longitude': 39.6068},
    'riyadh clock tower': {'name': 'Riyadh Clock Tower', 'city': 'Riyadh', 'latitude': 24.7136, 'longitude': 46.6753},
    'kingdom center': {'name': 'Kingdom Center', 'city': 'Riyadh', 'latitude': 24.7500, 'longitude': 46.7128},
    'burj al-mamlaka': {'name': 'Kingdom Center', 'city': 'Riyadh', 'latitude': 24.7500, 'longitude': 46.7128},
}

# Create blueprints
api_bp = Blueprint('api', __name__)

# Initialize AI modules
query_parser = QueryParser()
sentiment_analyzer = SentimentAnalyzer()
location_matcher = LocationMatcher()
recommendation_engine = RecommendationEngine()
distance_calculator = DistanceCalculator()

# Initialize Geoapify service (with fallback to database if API fails)
try:
    geoapify_service = GeoapifyService()
    USE_GEOAPIFY = True
    print("[OK] Geoapify service initialized - using real-time hotel data")
except Exception as e:
    geoapify_service = None
    USE_GEOAPIFY = False
    print(f"[WARN] Geoapify not available ({e}) - using database fallback")


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Hotel Booking AI API is running'
    }), 200


@api_bp.route('/chat', methods=['POST'])
def chat():
    """
    Main chatbot endpoint - Process user query and return hotel recommendations
    
    Expected JSON:
    {
        "message": "Find me a cheap hotel near Al-Haram with WiFi",
        "user_location": {"lat": 21.4225, "lng": 39.8262},  # Optional
        "last_search_context": {  # Optional - from conversation history
            "city": "Jeddah",
            "landmark": "Prophet's Mosque",
            "pricePreference": "affordable",
            "amenities": ["WiFi", "Parking"],
            "minRating": 4.0
        },
        "conversation_history": [...]  # Optional - last few messages
    }
    """
    try:
        data = request.get_json()
        print(f"[INFO] Received data: {data}")
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        user_location = data.get('user_location')
        last_search_context = data.get('last_search_context', {})  # Get conversation context
        
        print(f"[INFO] User message: {user_message}")
        print(f"[INFO] User location: {user_location}")
        if last_search_context:
            print(f"[INFO] Last search context: {last_search_context}")
        
        # Parse user query
        print("[INFO] Parsing query...")
        parsed_query = query_parser.parse(user_message)
        print(f"[OK] Parsed query: {parsed_query}")
        
        # **NEW**: Fill in missing fields from conversation context
        # BUT: If user explicitly mentions a NEW city, reset previous filters (price, rating)
        # to avoid carrying over unwanted filters to a new search
        
        # NEW: Handle "near me" FIRST - if user said "near me" with location, reverse-geocode and ignore context city
        user_said_near_me = ('near me' in user_message.lower() or 'around me' in user_message.lower())
        if user_said_near_me and user_location and not parsed_query.get('city'):
            print(f"[INFO] User said 'near me' - attempting to reverse-geocode location {user_location}")
            try:
                # Try to reverse geocode the user's location to get city name
                user_lat = float(user_location.get('lat', 0))
                user_lng = float(user_location.get('lng', 0))
                
                # Use geoapify to reverse geocode (get city name from coordinates)
                if USE_GEOAPIFY and geoapify_service:
                    city_name = geoapify_service.reverse_geocode((user_lat, user_lng))
                    if city_name:
                        parsed_query['city'] = city_name
                        print(f"[INFO] Reverse-geocoded user location to city: {city_name}")
            except Exception as e:
                print(f"[WARN] Reverse-geocoding failed: {e}")
        
        # Normalize for comparison (handle case sensitivity and spaces)
        parsed_city = parsed_query.get('city')
        context_city = last_search_context.get('city')
        city_changed = False
        
        if parsed_city and context_city:
            city_changed = parsed_city.lower().strip() != context_city.lower().strip()
        elif parsed_city and not context_city:
            city_changed = True  # First search, so "new city"
        
        # Track if we added city from context (user didn't mention a city, but we're using previous city)
        city_from_context = False
        
        # If user says "cheaper" but doesn't mention a city and did NOT say "near me", use the last city searched
        if not parsed_query.get('city') and last_search_context.get('city') and not user_said_near_me:
            parsed_query['city'] = last_search_context['city']
            city_from_context = True
            print(f"[INFO] Using city from context: {parsed_query['city']}")
        
        # Only carry over price/rating filters if NOT searching in a new city
        if not city_changed:
            if not parsed_query.get('price_preference') and last_search_context.get('pricePreference'):
                parsed_query['price_preference'] = last_search_context['pricePreference']
                print(f"[INFO] Using price preference from context: {parsed_query['price_preference']}")
        else:
            # User mentioned a new city - reset price filter AND landmark from context
            print(f"[INFO] New city detected ({parsed_query.get('city')}), resetting price filters and landmark")
        
        # Only carry over landmark if:
        # 1. NOT searching in a new city (city_changed = False)
        # 2. AND we didn't just add the city from context (to avoid landmark mismatch)
        # 3. AND the landmark's city matches the search city (if landmark has city info)
        if not parsed_query.get('landmark') and last_search_context.get('landmark') and not city_changed and not city_from_context:
            # Handle landmark from context - it might be a dict with 'name' and 'city' key
            context_landmark = last_search_context['landmark']
            landmark_city = None
            landmark_name = None
            
            if isinstance(context_landmark, dict):
                landmark_name = context_landmark.get('name')
                landmark_city = context_landmark.get('city')  # Get city from landmark if available
            else:
                landmark_name = context_landmark
            
            # Only use landmark if its city matches current search city (or city info not available)
            current_search_city = parsed_query.get('city')
            if landmark_city and current_search_city:
                # Both have city info - only carry over if cities match
                if landmark_city.lower().strip() == current_search_city.lower().strip():
                    parsed_query['landmark'] = landmark_name
                    print(f"[INFO] Using landmark from context: {landmark_name} (city matches)")
                else:
                    print(f"[INFO] Ignoring landmark from context - city mismatch ({landmark_city} vs {current_search_city})")
            elif not landmark_city:
                # Landmark doesn't have city info, so use it anyway
                parsed_query['landmark'] = landmark_name
        
        # Handle different intents
        intent = parsed_query['intent']
        
        if intent == 'greeting':
            return jsonify({
                'intent': 'greeting',
                'message': 'Hello! I can help you find the perfect hotel. Try asking: "Find me a hotel near Al-Haram" or "Show me luxury hotels in Riyadh"'
            }), 200
        
        if intent == 'help':
            return jsonify({
                'intent': 'help',
                'message': 'I can help you find hotels by:\n- Location (city or landmark)\n- Price range (cheap, affordable, luxury)\n- Amenities (WiFi, Pool, Gym)\n- Star rating\n\nTry: "Find affordable hotels near the Prophet\'s Mosque with parking"'
            }), 200
        
        if intent != 'search':
            return jsonify({
                'intent': 'unknown',
                'message': 'I\'m not sure what you\'re looking for. Try asking for hotel recommendations!'
            }), 200
        
        # Get search filters from parsed query
        filters = query_parser.get_search_filters(parsed_query)
        
        # If landmark mentioned, get its coordinates from hardcoded LANDMARKS
        reference_point = None
        landmark_name = None
        landmark_city = None  # Track landmark's city for context
        
        if parsed_query.get('landmark'):
            # Ensure landmark is a string (extract from dict if necessary)
            landmark_input = parsed_query['landmark']
            if isinstance(landmark_input, dict):
                landmark_query = landmark_input.get('name', '').lower().strip()
            else:
                landmark_query = str(landmark_input).lower().strip()
            
            print(f"[INFO] Looking for landmark: {landmark_query}")
            
            # 1. Try Database Search First
            try:
                db_landmark = get_landmark_by_name(landmark_query)
                if db_landmark:
                    landmark_name = db_landmark['name']
                    landmark_city = db_landmark.get('city')
                    reference_point = (float(db_landmark['latitude']), float(db_landmark['longitude']))
                    filters['city'] = db_landmark.get('city')
                    print(f"[OK] Found landmark in DB: {landmark_name} at {reference_point}")
            except Exception as e:
                print(f"[WARN] Database landmark search failed: {e}")

            # 2. Fallback to Hardcoded LANDMARKS if not found in DB
            if not reference_point:
                # First try exact match
                if landmark_query in LANDMARKS:
                    landmark = LANDMARKS[landmark_query]
                    landmark_name = landmark['name']
                    landmark_city = landmark.get('city')
                    reference_point = (landmark['latitude'], landmark['longitude'])
                    filters['city'] = landmark.get('city')
                    print(f"[OK] Found landmark: {landmark_name} at {reference_point}")
                else:
                    # Try fuzzy matching on landmark names
                    from fuzzywuzzy import fuzz
                    best_match = None
                    best_score = 0
                    
                    for key, landmark in LANDMARKS.items():
                        score = fuzz.ratio(landmark_query, key)
                        if score > best_score:
                            best_score = score
                            best_match = (key, landmark)
                    
                    if best_match and best_score > 60:
                        key, landmark = best_match
                        landmark_name = landmark['name']
                        landmark_city = landmark.get('city')
                        reference_point = (landmark['latitude'], landmark['longitude'])
                        filters['city'] = landmark.get('city')
                        print(f"[OK] Fuzzy matched landmark: {landmark_name} (score: {best_score})")
                    else:
                        print(f"[WARN] No landmark match found for: {landmark_query}")
        
        # Search for hotels - Combine BOTH Geoapify (real-time) and Database (accurate data)
        hotels = []
        search_location = reference_point
        geoapify_hotels = []
        db_hotels = []
        
        # If no landmark but city mentioned, geocode the city
        if not search_location and USE_GEOAPIFY and geoapify_service and filters.get('city'):
            print(f"[INFO] Geocoding city: {filters['city']}")
            try:
                # Geocode city name (works worldwide)
                city_coords = geoapify_service.geocode_address(filters['city'])
                if city_coords:
                    search_location = city_coords
                    print(f"[OK] City coordinates: {search_location}")
            except Exception as e:
                print(f"[WARN] Geocoding failed: {e}")
        
        # Get Geoapify hotels if available
        if USE_GEOAPIFY and geoapify_service and search_location:
            try:
                geoapify_results = geoapify_service.search_hotels_nearby(
                    location=search_location,
                    radius=5000,  # 5km radius
                    keyword="hotel",  # Search for hotels, not filtered by price (we filter after)
                    limit=50
                )
                
                # Convert Geoapify format to our standard format
                for gh in geoapify_results:
                    # Skip hotels with no name or empty name
                    hotel_name = gh.get('name', '').strip()
                    if not hotel_name:
                        print(f"[SKIP] Skipping hotel with no name")
                        continue
                    
                    # Determine star rating with fallback logic
                    star_rating = gh['rating']
                    has_website = bool(gh.get('website', '').strip())
                    
                    # If default rating (no real data), apply fallback logic
                    if star_rating == 3.0:
                        # Check for fancy/luxury keywords in hotel name
                        fancy_keywords = ['luxury', 'premium', 'royal', 'palace', 'grand', 'heritage', 
                                        'elite', 'exclusive', 'deluxe', 'resort', 'villa', 'ritz', 
                                        'hilton', 'marriott', 'intercontinental', 'sheraton', 'four seasons',
                                        'بقصر', 'قصر', 'الملكي', 'الفندقي', 'فندق فاخر']
                        
                        hotel_name_lower = hotel_name.lower()
                        has_fancy_name = any(keyword in hotel_name_lower for keyword in fancy_keywords)
                        
                        if has_fancy_name and has_website:
                            # Fancy name + website = 5 stars
                            star_rating = 5.0
                            print(f"[RATING] {hotel_name}: 5 stars (fancy name + website)")
                        elif has_website:
                            # Website only = 4 stars
                            star_rating = 4.0
                            print(f"[RATING] {hotel_name}: 4 stars (website available)")
                        # else: keep default 3.0
                    
                    # Estimate price based on star rating
                    if star_rating >= 4.5:
                        estimated_price = 1000  # 5-star luxury
                    elif star_rating >= 4.0:
                        estimated_price = 700  # 4-4.5 star
                    elif star_rating >= 3.5:
                        estimated_price = 500  # 3.5-4 star
                    elif star_rating >= 3.0:
                        estimated_price = 350  # 3-3.5 star
                    else:
                        estimated_price = 250  # Below 3 star
                    
                    # Extract amenities from Geoapify categories
                    amenities = []
                    categories = gh.get('categories', [])
                    
                    # Map Geoapify categories to user-friendly amenities
                    for category in categories:
                        category_lower = category.lower()
                        
                        # Internet/WiFi amenities
                        if 'internet_access' in category_lower or 'wifi' in category_lower:
                            if 'WiFi' not in amenities:
                                amenities.append('WiFi')
                        # Wheelchair accessibility
                        elif 'wheelchair' in category_lower and 'yes' in category_lower:
                            if 'Wheelchair Accessible' not in amenities:
                                amenities.append('Wheelchair Accessible')
                        # Parking
                        elif 'parking' in category_lower:
                            if 'Parking' not in amenities:
                                amenities.append('Parking')
                        # Pool/Swimming
                        elif 'pool' in category_lower or 'swimming' in category_lower:
                            if 'Pool' not in amenities:
                                amenities.append('Pool')
                        # Gym/Fitness
                        elif 'gym' in category_lower or 'fitness' in category_lower:
                            if 'Gym' not in amenities:
                                amenities.append('Gym')
                        # Spa/Wellness
                        elif 'spa' in category_lower or 'wellness' in category_lower:
                            if 'Spa' not in amenities:
                                amenities.append('Spa')
                        # Restaurant
                        elif 'restaurant' in category_lower:
                            if 'Restaurant' not in amenities:
                                amenities.append('Restaurant')
                        # Bar
                        elif 'bar' in category_lower:
                            if 'Bar' not in amenities:
                                amenities.append('Bar')
                    
                    # If no specific amenities found, add generic ones based on hotel type
                    if not amenities:
                        # Most hotels have WiFi and restaurants
                        amenities = ['WiFi', 'Restaurant']
                    
                    geoapify_hotels.append({
                        'id': hash(gh['geoapify_place_id']) % 100000,  # Generate numeric ID
                        'name': hotel_name,
                        'address': gh['address'],
                        'city': gh.get('city', filters.get('city', '')),
                        'latitude': gh['latitude'],
                        'longitude': gh['longitude'],
                        'star_rating': star_rating,
                        'price_per_night': estimated_price,  # Estimated based on rating
                        'amenities': amenities,  # Extracted from Geoapify categories
                        'description': f"Located in {gh.get('city', 'the area')}",
                        'phone': gh.get('phone', ''),
                        'website': gh.get('website', ''),
                        'source': 'geoapify'
                    })
                
                print(f"[OK] Found {len(geoapify_hotels)} hotels from Geoapify")
                
            except Exception as e:
                print(f"[WARN] Geoapify search failed: {e}")
        
        # Also get database hotels for accurate ratings and data
        if filters.get('city'):
            print(f"[INFO] Also searching database for {filters['city']}...")
            try:
                db_hotels = get_hotels_by_city(filters['city'])
                print(f"[OK] Found {len(db_hotels)} hotels from database")
            except Exception as e:
                print(f"[WARN] Database search failed: {e}")
        
        # Combine both sources - database hotels first (more accurate), then Geoapify (for additional options)
        hotels = db_hotels + geoapify_hotels
        print(f"[OK] Total hotels available: {len(hotels)} (Database: {len(db_hotels)}, Geoapify: {len(geoapify_hotels)})")
        

        # Use reference_point for distance calculation (landmark takes priority, then city, then user location)
        if not reference_point:
            reference_point = search_location
        
        # Filter hotels based on user preferences (price preference and minimum rating)
        if hotels:
            price_preference_raw = parsed_query.get('price_preference')
            price_preference = price_preference_raw.lower() if price_preference_raw else ''
            min_rating = float(parsed_query.get('min_rating', 0)) if parsed_query.get('min_rating') else 0
            
            # Sort hotels by star rating (descending) to prioritize highly-rated ones
            hotels_with_ratings = []
            for hotel in hotels:
                star_rating = hotel.get('star_rating')
                
                # Skip hotels without rating
                if star_rating is None:
                    star_rating = 3.0  # Default to 3 stars if unknown
                
                star_rating = float(star_rating)
                hotel['star_rating'] = star_rating  # Update hotel with numeric rating
                hotels_with_ratings.append((hotel, star_rating))
            
            # Sort by rating (highest first) - this gives us best hotels first regardless of preference
            hotels_with_ratings.sort(key=lambda x: x[1], reverse=True)
            hotels = [h[0] for h in hotels_with_ratings]
            
            # Filter by minimum rating only
            if min_rating > 0:
                hotels = [h for h in hotels if h.get('star_rating', 3.0) >= min_rating]
            
            # For price preferences, filter and show accordingly
            if price_preference == 'high':
                # Luxury preference: Strictly filter for 4+ star hotels
                luxury_hotels = [h for h in hotels if h.get('star_rating', 0) >= 4.0]
                
                if luxury_hotels:
                    print(f"[INFO] Showing {len(luxury_hotels)} luxury hotels (4+ stars)")
                    hotels = luxury_hotels[:10]
                else:
                    # Fallback if no luxury hotels found
                    print(f"[INFO] No 4+ star hotels found, showing top-rated available")
                    hotels = hotels[:10]
                    
            elif price_preference == 'low':
                # Budget preference: Show lowest-priced (which are lowest-rated 2-3 star)
                hotels.reverse()  # Reverse to show lowest-rated first
                print(f"[INFO] Showing budget hotels (lowest-rated first)")
                hotels = hotels[:10]
                hotels.reverse()  # Reverse back so lowest-priced (budgeted) are at top
            else:
                # No preference or medium: show top-rated hotels
                print(f"[INFO] Showing all hotels (no strong price preference)")
                hotels = hotels[:10]
        
        if not hotels:
            return jsonify({
                'intent': 'search',
                'message': 'Sorry, I couldn\'t find any hotels matching your criteria. Try adjusting your search.',
                'filters_used': parsed_query,
                'hotels': []
            }), 200
        
        # Add distances
        #  - distance_from_reference: distance to the landmark/city used as the search center (if any)
        #  - distance_from_user: distance from the user's actual location (if provided)
        if reference_point:
            hotels = distance_calculator.add_distances_to_hotels(hotels, reference_point)

        # Always calculate distance from user (if available) so frontend can show accurate user-to-hotel distance
        if user_location and 'lat' in user_location and 'lng' in user_location:
            user_point = (float(user_location['lat']), float(user_location['lng']))
            for hotel in hotels:
                try:
                    hotel_point = (float(hotel['latitude']), float(hotel['longitude']))
                    hotel['distance_from_user'] = distance_calculator.calculate_distance(user_point, hotel_point)
                except Exception:
                    hotel['distance_from_user'] = None
        
        # Get recommendations
        user_preferences = {
            'price_preference': parsed_query.get('price_preference'),
            'min_rating': parsed_query.get('min_rating'),
            'requested_amenities': parsed_query.get('amenities', [])
        }
        
        # Adjust weights based on user preferences
        # If user specified a rating preference (luxury, top-rated, etc), boost rating weight SIGNIFICANTLY
        custom_weights = None
        if parsed_query.get('min_rating'):
            custom_weights = {
                'distance': 0.15,    # 15% - Proximity is less important
                'price': 0.15,       # 15% - Price match is less important
                'rating': 0.60,      # 60% - Rating DOMINATES when user asks for quality
                'amenities': 0.10    # 10% - Amenity match
            }
            print(f"[INFO] Using HIGH RATING WEIGHT for quality search (min_rating: {parsed_query.get('min_rating')})")
        elif parsed_query.get('price_preference'):
            # If only price preference, boost price weight
            custom_weights = {
                'distance': 0.25,
                'price': 0.45,       # 45% - Price is more important
                'rating': 0.20,
                'amenities': 0.10
            }
        
        # Use custom weights if specified, otherwise use default
        if custom_weights:
            custom_engine = RecommendationEngine(weights=custom_weights)
            recommendations = custom_engine.get_top_recommendations(
                hotels,
                user_preferences,
                count=15
            )
        else:
            recommendations = recommendation_engine.get_top_recommendations(
                hotels,
                user_preferences,
                count=15
            )
        
        # CRITICAL FILTER: If user asked for a specific rating (top-rated, luxury, etc),
        # filter out hotels that don't meet the minimum rating threshold
        # BUT if NO hotels meet it, lower threshold intelligently
        if parsed_query.get('min_rating'):
            min_rating = parsed_query.get('min_rating')
            original_min_rating = min_rating
            
            # First try to filter at the requested level
            filtered_recommendations = [h for h in recommendations if float(h.get('star_rating', 0)) >= min_rating]
            
            # If no results, intelligently lower the threshold
            if not filtered_recommendations:
                print(f"[WARN] No hotels found at {min_rating}+ stars, intelligently lowering threshold...")
                
                # Try each lower rating tier
                for fallback_rating in [4.5, 4.0, 3.5, 3.0]:
                    filtered_recommendations = [h for h in recommendations if float(h.get('star_rating', 0)) >= fallback_rating]
                    if filtered_recommendations:
                        print(f"[INFO] Found {len(filtered_recommendations)} hotels at {fallback_rating}+ stars instead")
                        print(f"[INFO] User asked for {original_min_rating}+ stars but only {fallback_rating}+ available in {filters.get('city')}")
                        break
                
                # If still no results, show all available sorted by rating
                if not filtered_recommendations:
                    filtered_recommendations = sorted(recommendations, key=lambda h: float(h.get('star_rating', 0)), reverse=True)
                    print(f"[INFO] Showing all available hotels sorted by rating (max {filtered_recommendations[0].get('star_rating')} stars)")
            
            recommendations = filtered_recommendations
            print(f"[INFO] Final hotel count after rating filter: {len(recommendations)} hotels")
        
        # Format response
        formatted_hotels = []
        for hotel in recommendations:
            formatted = {
                'id': hotel['id'],
                'name': hotel['name'],
                'address': hotel.get('address', ''),
                'city': hotel.get('city', ''),
                'star_rating': hotel.get('star_rating', 0),
                'price_per_night': hotel.get('price_per_night', None),
                'amenities': hotel.get('amenities', []),
                'coordinates': {
                    'lat': float(hotel.get('latitude')) if hotel.get('latitude') is not None else None,
                    'lng': float(hotel.get('longitude')) if hotel.get('longitude') is not None else None
                },
                'recommendation_score': hotel.get('recommendation_score', 0),
                'score_breakdown': hotel.get('score_breakdown', {}),
                'explanation': recommendation_engine.explain_recommendation(hotel),
                'phone': hotel.get('phone', ''),
                'website': hotel.get('website', '')
            }

            # Prefer showing distance from the user if available; otherwise show distance from the search reference (landmark/city)
            if 'distance_from_user' in hotel and hotel['distance_from_user'] is not None:
                formatted['distance'] = distance_calculator.format_distance(hotel['distance_from_user'])
            elif 'distance_from_reference' in hotel:
                formatted['distance'] = distance_calculator.format_distance(hotel['distance_from_reference'])
            
            formatted_hotels.append(formatted)
        
        # Generate response message
        response_message = f"I found {len(recommendations)} hotels"
        if landmark_name:
            response_message += f" near {landmark_name}"
        elif parsed_query.get('city'):
            response_message += f" in {parsed_query['city']}"
        response_message += " matching your preferences:"
        
        return jsonify({
            'intent': 'search',
            'message': response_message,
            'filters_used': parsed_query,
            'landmark': {'name': landmark_name, 'city': landmark_city, 'coordinates': reference_point} if landmark_name else None,
            'hotels': formatted_hotels,
            'total_found': len(hotels)
        }), 200
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Error in /api/chat:")
        error_traceback = traceback.format_exc()
        print(error_traceback)
        
        # Try to extract the problematic line for debugging
        tb_lines = error_traceback.split('\n')
        for i, line in enumerate(tb_lines):
            if '.lower()' in line or 'NoneType' in line:
                print(f"[DEBUG] Problematic line {i}: {line}")
        
        return jsonify({
            'error': 'An error occurred processing your request',
            'details': str(e),
            'traceback': error_traceback  # Full traceback for debugging
        }), 500


@api_bp.route('/hotels', methods=['GET'])
def get_hotels():
    """Get all hotels or filter by city"""
    try:
        city = request.args.get('city')
        
        if city:
            hotels = get_hotels_by_city(city)
        else:
            hotels = get_all_hotels()
        
        return jsonify({
            'hotels': hotels,
            'count': len(hotels)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/hotels/<int:hotel_id>', methods=['GET'])
def get_hotel_details(hotel_id):
    """Get detailed information about a specific hotel"""
    try:
        hotel = get_hotel_by_id(hotel_id)
        
        if not hotel:
            return jsonify({'error': 'Hotel not found'}), 404
        
        # Get reviews
        reviews = get_reviews_by_hotel_id(hotel_id)
        
        # Analyze sentiment of reviews
        if reviews:
            sentiment_data = sentiment_analyzer.analyze_reviews(reviews)
            review_summary = sentiment_analyzer.generate_summary(sentiment_data)
        else:
            sentiment_data = None
            review_summary = "No reviews available yet."
        
        return jsonify({
            'hotel': hotel,
            'reviews': reviews,
            'review_count': len(reviews),
            'sentiment_analysis': sentiment_data,
            'review_summary': review_summary
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/hotels/nearby', methods=['POST'])
def get_nearby_hotels():
    """
    Get hotels near a location
    
    Expected JSON:
    {
        "latitude": 21.4225,
        "longitude": 39.8262,
        "radius_km": 5,
        "count": 10
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        lat = float(data['latitude'])
        lng = float(data['longitude'])
        radius = float(data.get('radius_km', 5))
        count = int(data.get('count', 10))
        
        reference_point = (lat, lng)
        
        # Get all hotels
        all_hotels = get_all_hotels()
        
        # Filter by radius
        nearby_hotels = distance_calculator.filter_by_radius(
            all_hotels,
            reference_point,
            radius
        )
        
        # Sort by distance and limit
        nearby_hotels = distance_calculator.sort_by_distance(
            nearby_hotels,
            reference_point
        )[:count]
        
        # Format distances
        for hotel in nearby_hotels:
            if 'distance_from_reference' in hotel:
                hotel['distance_formatted'] = distance_calculator.format_distance(
                    hotel['distance_from_reference']
                )
        
        return jsonify({
            'hotels': nearby_hotels,
            'count': len(nearby_hotels),
            'search_radius': f"{radius} km"
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/landmarks', methods=['GET'])
def get_landmarks():
    """Get all landmarks"""
    try:
        from database.db_connection import DatabaseConnection
        
        db = DatabaseConnection()
        landmarks = db.execute_query("SELECT * FROM landmarks")
        db.disconnect()
        
        formatted_landmarks = []
        for landmark in landmarks:
            formatted_landmarks.append({
                'id': landmark['id'],
                'name': landmark['name'],
                'latitude': float(landmark['latitude']),
                'longitude': float(landmark['longitude']),
                'city': landmark['city'],
                'description': landmark['description']
            })
        
        return jsonify({
            'landmarks': formatted_landmarks,
            'count': len(formatted_landmarks)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

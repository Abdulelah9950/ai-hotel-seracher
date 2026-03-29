# Google Places API Integration
# Fetch real hotels from Google Places API

import googlemaps
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_MAPS_API_KEY


class GooglePlacesService:
    """
    Service to fetch real hotels from Google Places API
    """
    
    def __init__(self):
        """Initialize Google Maps client"""
        self.gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    
    def search_hotels_nearby(self, location, radius=5000, keyword=None, min_price=None, max_price=None):
        """
        Search for hotels near a location
        
        Args:
            location (tuple): (latitude, longitude)
            radius (int): Search radius in meters (default 5km)
            keyword (str): Additional keyword filter (e.g., "luxury", "budget")
            min_price (int): Minimum price level (0-4)
            max_price (int): Maximum price level (0-4)
            
        Returns:
            list: List of hotel dictionaries
        """
        try:
            # Search for hotels
            places_result = self.gmaps.places_nearby(
                location=location,
                radius=radius,
                type='lodging',
                keyword=keyword
            )
            
            hotels = []
            for place in places_result.get('results', []):
                # Get place details
                place_details = self.gmaps.place(
                    place_id=place['place_id'],
                    fields=['name', 'formatted_address', 'geometry', 'rating', 
                           'price_level', 'photos', 'formatted_phone_number',
                           'website', 'opening_hours', 'types']
                )
                
                details = place_details.get('result', {})
                
                # Extract hotel data
                hotel = {
                    'google_place_id': place['place_id'],
                    'name': details.get('name'),
                    'address': details.get('formatted_address'),
                    'latitude': details['geometry']['location']['lat'],
                    'longitude': details['geometry']['location']['lng'],
                    'rating': details.get('rating'),  # Google user rating (1-5)
                    'price_level': details.get('price_level'),  # 0-4 scale
                    'phone': details.get('formatted_phone_number'),
                    'website': details.get('website'),
                    'photo_reference': place.get('photos', [{}])[0].get('photo_reference') if place.get('photos') else None
                }
                
                # Filter by price if specified
                if min_price is not None and hotel['price_level'] and hotel['price_level'] < min_price:
                    continue
                if max_price is not None and hotel['price_level'] and hotel['price_level'] > max_price:
                    continue
                
                hotels.append(hotel)
            
            return hotels
            
        except Exception as e:
            print(f"Error searching Google Places: {e}")
            return []
    
    def get_hotel_details(self, place_id):
        """
        Get detailed information about a specific hotel
        
        Args:
            place_id (str): Google Place ID
            
        Returns:
            dict: Hotel details
        """
        try:
            place_details = self.gmaps.place(
                place_id=place_id,
                fields=['name', 'formatted_address', 'geometry', 'rating',
                       'price_level', 'photos', 'formatted_phone_number',
                       'website', 'opening_hours', 'reviews', 'types',
                       'international_phone_number', 'url']
            )
            
            return place_details.get('result', {})
            
        except Exception as e:
            print(f"Error fetching hotel details: {e}")
            return {}
    
    def calculate_distance(self, origin, destination):
        """
        Calculate distance between two points using Google Distance Matrix API
        
        Args:
            origin (tuple): (latitude, longitude)
            destination (tuple): (latitude, longitude)
            
        Returns:
            dict: Distance information {distance_km, duration_minutes}
        """
        try:
            result = self.gmaps.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode='driving'
            )
            
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                element = result['rows'][0]['elements'][0]
                return {
                    'distance_km': element['distance']['value'] / 1000,  # Convert to km
                    'distance_text': element['distance']['text'],
                    'duration_minutes': element['duration']['value'] / 60,  # Convert to minutes
                    'duration_text': element['duration']['text']
                }
            
            return None
            
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return None
    
    def geocode_address(self, address):
        """
        Convert address to coordinates
        
        Args:
            address (str): Address to geocode
            
        Returns:
            tuple: (latitude, longitude) or None
        """
        try:
            result = self.gmaps.geocode(address)
            if result:
                location = result[0]['geometry']['location']
                return (location['lat'], location['lng'])
            return None
            
        except Exception as e:
            print(f"Error geocoding address: {e}")
            return None
    
    def get_photo_url(self, photo_reference, max_width=400):
        """
        Get photo URL from photo reference
        
        Args:
            photo_reference (str): Photo reference from Places API
            max_width (int): Maximum width of photo
            
        Returns:
            str: Photo URL
        """
        if not photo_reference:
            return None
        
        return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photoreference={photo_reference}&key={GOOGLE_MAPS_API_KEY}"


# Example usage
if __name__ == '__main__':
    service = GooglePlacesService()
    
    # Search for hotels near Al-Haram in Makkah
    makkah_location = (21.4225, 39.8262)
    hotels = service.search_hotels_nearby(makkah_location, radius=3000, keyword="hotel")
    
    print(f"Found {len(hotels)} hotels:")
    for hotel in hotels[:5]:  # Show first 5
        print(f"- {hotel['name']}: {hotel['address']}")
        print(f"  Rating: {hotel['rating']}, Price Level: {hotel['price_level']}")

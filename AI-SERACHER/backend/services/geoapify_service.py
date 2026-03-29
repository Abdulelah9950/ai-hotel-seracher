"""
Geoapify Places API Service
Free alternative to Google Places API
Free tier: 3000 requests/day, no credit card needed
"""

import requests
from typing import List, Dict, Tuple, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GEOAPIFY_API_KEY


class GeoapifyService:
    """
    Service class for Geoapify Places API
    Free tier: 3000 requests/day with no credit card required
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Geoapify service
        
        Args:
            api_key (str): Geoapify API key. If None, uses config.GEOAPIFY_API_KEY
        """
        self.api_key = api_key or GEOAPIFY_API_KEY
        self.base_url = "https://api.geoapify.com/v2"
        
        if not self.api_key:
            raise ValueError("Geoapify API key is required. Set GEOAPIFY_API_KEY in .env file")
    
    def search_hotels_nearby(
        self,
        location: Tuple[float, float],
        radius: int = 5000,
        keyword: str = None,
        min_price: int = None,
        max_price: int = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search for hotels near a location
        
        Args:
            location (tuple): (latitude, longitude) center point
            radius (int): Search radius in meters (default 5000m = 5km)
            keyword (str): Optional keyword filter (e.g., "luxury", "budget")
            min_price (int): Minimum price filter (not directly supported, for compatibility)
            max_price (int): Maximum price filter (not directly supported, for compatibility)
            limit (int): Maximum number of results (default 20)
        
        Returns:
            list: List of hotel dictionaries with standardized format
        """
        lat, lng = location
        
        # Geoapify Places API endpoint
        url = f"{self.base_url}/places"
        
        # Build categories for hotels/accommodations
        categories = "accommodation.hotel,accommodation"
        
        # Build filter string
        filters = f"circle:{lng},{lat},{radius}"
        
        params = {
            "categories": categories,
            "filter": filters,
            "limit": limit,
            "apiKey": self.api_key
        }
        
        # Add keyword as text filter if provided
        if keyword:
            params["text"] = keyword
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            hotels = []
            
            # Parse results
            for place in data.get('features', []):
                props = place.get('properties', {})
                coords = place.get('geometry', {}).get('coordinates', [None, None])
                
                # Extract hotel information
                hotel = {
                    'geoapify_place_id': props.get('place_id', ''),
                    'name': props.get('name', 'Unknown Hotel'),
                    'address': props.get('formatted', props.get('address_line1', '')),
                    'city': props.get('city', ''),
                    'country': props.get('country', ''),
                    'latitude': coords[1] if len(coords) > 1 else None,
                    'longitude': coords[0] if len(coords) > 0 else None,
                    'rating': self._extract_rating(props),
                    'categories': props.get('categories', []),
                    'website': props.get('website', ''),
                    'phone': props.get('contact', {}).get('phone', ''),
                    'datasource': props.get('datasource', {}).get('raw', {}),
                }
                
                # Only add if we have valid coordinates
                if hotel['latitude'] and hotel['longitude']:
                    hotels.append(hotel)
            
            print(f"[OK] Found {len(hotels)} hotels near ({lat}, {lng})")
            return hotels
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error fetching hotels from Geoapify: {e}")
            return []
    
    def get_hotel_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific place
        
        Args:
            place_id (str): Geoapify place ID
        
        Returns:
            dict: Detailed hotel information or None
        """
        url = f"{self.base_url}/place-details"
        
        params = {
            "id": place_id,
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            features = data.get('features', [])
            
            if features:
                place = features[0]
                props = place.get('properties', {})
                coords = place.get('geometry', {}).get('coordinates', [None, None])
                
                return {
                    'geoapify_place_id': props.get('place_id', ''),
                    'name': props.get('name', 'Unknown'),
                    'address': props.get('formatted', ''),
                    'city': props.get('city', ''),
                    'latitude': coords[1] if len(coords) > 1 else None,
                    'longitude': coords[0] if len(coords) > 0 else None,
                    'rating': self._extract_rating(props),
                    'website': props.get('website', ''),
                    'phone': props.get('contact', {}).get('phone', ''),
                    'opening_hours': props.get('opening_hours', ''),
                    'datasource': props.get('datasource', {})
                }
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error fetching place details: {e}")
            return None
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates
        
        Args:
            address (str): Address string
        
        Returns:
            tuple: (latitude, longitude) or None
        """
        url = "https://api.geoapify.com/v1/geocode/search"
        
        params = {
            "text": address,
            "apiKey": self.api_key,
            "limit": 1
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            features = data.get('features', [])
            
            if features:
                coords = features[0].get('geometry', {}).get('coordinates', [])
                if len(coords) >= 2:
                    return (coords[1], coords[0])  # Return (lat, lng)
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error geocoding address: {e}")
            return None
    
    def reverse_geocode(self, location: Tuple[float, float]) -> Optional[str]:
        """
        Convert coordinates to city name (for "near me" queries)
        
        Args:
            location (tuple): (latitude, longitude)
        
        Returns:
            str: City name or None
        """
        lat, lng = location
        url = "https://api.geoapify.com/v1/geocode/reverse"
        
        params = {
            "lat": lat,
            "lon": lng,
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            features = data.get('features', [])
            
            if features:
                props = features[0].get('properties', {})
                # Try to get city name from properties
                city = props.get('city') or props.get('town') or props.get('state_district')
                if city:
                    return city
                # Fallback to formatted address if city not available
                return props.get('formatted', '')
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error reverse geocoding: {e}")
            return None
    
    def _extract_rating(self, properties: Dict) -> float:
        """
        Extract rating from various possible fields
        
        Args:
            properties (dict): Place properties
        
        Returns:
            float: Rating value (0-5)
        """
        # Try different rating sources
        datasource = properties.get('datasource', {}).get('raw', {})
        
        # Try stars field (common for hotels)
        stars = datasource.get('stars', 0)
        if stars and isinstance(stars, (int, float)):
            return float(stars)
        
        # Try rating field
        rating = datasource.get('rating', 0)
        if rating and isinstance(rating, (int, float)):
            return float(rating)
        
        # Default to 3.0 if no rating available
        return 3.0


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Geoapify Service")
    print("=" * 60)
    
    try:
        service = GeoapifyService()
        
        # Test 1: Search hotels near Al-Haram, Makkah
        print("\n📍 Test 1: Hotels near Al-Haram, Makkah")
        print("-" * 60)
        makkah_location = (21.4225, 39.8262)
        hotels = service.search_hotels_nearby(makkah_location, radius=5000, limit=5)
        
        if hotels:
            print(f"[OK] Found {len(hotels)} hotels:")
            for i, hotel in enumerate(hotels, 1):
                print(f"\n{i}. {hotel['name']}")
                print(f"   Address: {hotel['address']}")
                print(f"   Rating: {hotel['rating']}")
                print(f"   Phone: {hotel['phone'] or 'N/A'}")
                print(f"   Website: {hotel['website'] or 'N/A'}")
        else:
            print("[WARN] No hotels found")
        
        # Test 2: Geocoding
        print("\n\n📍 Test 2: Geocode 'Riyadh, Saudi Arabia'")
        print("-" * 60)
        coords = service.geocode_address("Riyadh, Saudi Arabia")
        if coords:
            print(f"[OK] Coordinates: {coords[0]:.4f}, {coords[1]:.4f}")
        else:
            print("[ERROR] Geocoding failed")
        
        # Test 3: Reverse geocoding
        print("\n\n📍 Test 3: Reverse geocode Al-Haram coordinates")
        print("-" * 60)
        address = service.reverse_geocode(makkah_location)
        if address:
            print(f"[OK] Address: {address}")
        else:
            print("[ERROR] Reverse geocoding failed")
        
        print("\n" + "=" * 60)
        print("[OK] All tests completed!")
        
    except ValueError as e:
        print(f"\n[ERROR] Configuration Error: {e}")
        print("\n💡 To fix this:")
        print("1. Sign up at https://www.geoapify.com/")
        print("2. Get your free API key")
        print("3. Add to backend/.env file:")
        print("   GEOAPIFY_API_KEY=your_key_here")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

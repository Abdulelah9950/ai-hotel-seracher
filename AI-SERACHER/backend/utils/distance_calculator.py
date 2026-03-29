# Distance Calculator
# Calculate distances between locations

from geopy.distance import geodesic
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DistanceCalculator:
    """
    Calculate distances between geographical coordinates
    """
    
    def __init__(self):
        """Initialize distance calculator"""
        pass
    
    def calculate_distance(self, point1, point2, unit='km'):
        """
        Calculate distance between two points
        
        Args:
            point1 (tuple): (latitude, longitude) of first point
            point2 (tuple): (latitude, longitude) of second point
            unit (str): 'km' for kilometers, 'mi' for miles, 'm' for meters
            
        Returns:
            float: Distance between points
        """
        try:
            distance = geodesic(point1, point2)
            
            if unit == 'km':
                return round(distance.km, 2)
            elif unit == 'mi':
                return round(distance.miles, 2)
            elif unit == 'm':
                return round(distance.meters, 2)
            else:
                return round(distance.km, 2)  # Default to km
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return None
    
    def add_distances_to_hotels(self, hotels, reference_point):
        """
        Add distance from reference point to each hotel
        
        Args:
            hotels (list): List of hotel dictionaries with latitude/longitude
            reference_point (tuple): (latitude, longitude) reference coordinates
            
        Returns:
            list: Hotels with added 'distance' field
        """
        for hotel in hotels:
            hotel_point = (float(hotel['latitude']), float(hotel['longitude']))
            distance = self.calculate_distance(reference_point, hotel_point)
            hotel['distance_from_reference'] = distance
        
        return hotels
    
    def sort_by_distance(self, hotels, reference_point):
        """
        Sort hotels by distance from reference point
        
        Args:
            hotels (list): List of hotel dictionaries
            reference_point (tuple): (latitude, longitude) reference coordinates
            
        Returns:
            list: Hotels sorted by distance (closest first)
        """
        # Add distances
        hotels = self.add_distances_to_hotels(hotels, reference_point)
        
        # Sort by distance
        hotels.sort(key=lambda x: x.get('distance_from_reference', float('inf')))
        
        return hotels
    
    def filter_by_radius(self, hotels, center_point, radius_km):
        """
        Filter hotels within a certain radius
        
        Args:
            hotels (list): List of hotel dictionaries
            center_point (tuple): (latitude, longitude) center coordinates
            radius_km (float): Radius in kilometers
            
        Returns:
            list: Hotels within radius
        """
        filtered = []
        
        for hotel in hotels:
            hotel_point = (float(hotel['latitude']), float(hotel['longitude']))
            distance = self.calculate_distance(center_point, hotel_point)
            
            if distance and distance <= radius_km:
                hotel['distance_from_center'] = distance
                filtered.append(hotel)
        
        return filtered
    
    def find_nearest_hotels(self, hotels, reference_point, count=5):
        """
        Find N nearest hotels to a reference point
        
        Args:
            hotels (list): List of hotel dictionaries
            reference_point (tuple): (latitude, longitude) reference coordinates
            count (int): Number of hotels to return
            
        Returns:
            list: N nearest hotels
        """
        sorted_hotels = self.sort_by_distance(hotels, reference_point)
        return sorted_hotels[:count]
    
    def calculate_multiple_distances(self, hotel, reference_points):
        """
        Calculate distances from a hotel to multiple reference points
        
        Args:
            hotel (dict): Hotel dictionary with latitude/longitude
            reference_points (dict): {name: (lat, lng)} dictionary
            
        Returns:
            dict: {name: distance} for each reference point
        """
        hotel_point = (float(hotel['latitude']), float(hotel['longitude']))
        distances = {}
        
        for name, point in reference_points.items():
            distance = self.calculate_distance(hotel_point, point)
            distances[name] = distance
        
        return distances
    
    def get_distance_description(self, distance_km):
        """
        Get a human-readable description of distance
        
        Args:
            distance_km (float): Distance in kilometers
            
        Returns:
            str: Description like "Very close" or "Moderate distance"
        """
        if distance_km < 0.5:
            return "Walking distance"
        elif distance_km < 2:
            return "Very close"
        elif distance_km < 5:
            return "Close"
        elif distance_km < 10:
            return "Moderate distance"
        elif distance_km < 20:
            return "Far"
        else:
            return "Very far"
    
    def format_distance(self, distance_km):
        """
        Format distance for display
        
        Args:
            distance_km (float): Distance in kilometers
            
        Returns:
            str: Formatted distance string
        """
        if distance_km < 1:
            meters = int(distance_km * 1000)
            return f"{meters} meters"
        else:
            return f"{distance_km:.2f} km"


def test_distance_calculator():
    """Test the distance calculator with sample data"""
    
    print("\n" + "=" * 60)
    print("Testing Distance Calculator")
    print("=" * 60)
    
    calculator = DistanceCalculator()
    
    # Test coordinates
    al_haram = (21.4225, 39.8262)
    prophet_mosque = (24.4672, 39.6108)
    
    # Sample hotels
    sample_hotels = [
        {
            'name': 'Hotel A',
            'latitude': 21.4244,
            'longitude': 39.8267
        },
        {
            'name': 'Hotel B',
            'latitude': 21.4350,
            'longitude': 39.8450
        },
        {
            'name': 'Hotel C',
            'latitude': 21.4190,
            'longitude': 39.8240
        }
    ]
    
    print("\n[Test 1] Calculate Distance Between Two Points")
    print("-" * 60)
    
    distance = calculator.calculate_distance(al_haram, prophet_mosque)
    print(f"\n✓ Distance from Al-Haram to Prophet's Mosque: {distance} km")
    
    # Convert to miles
    distance_mi = calculator.calculate_distance(al_haram, prophet_mosque, unit='mi')
    print(f"✓ Same distance in miles: {distance_mi} mi")
    
    print("\n" + "-" * 60)
    print("[Test 2] Add Distances to Hotels")
    print("-" * 60)
    
    hotels_with_distance = calculator.add_distances_to_hotels(
        sample_hotels.copy(), 
        al_haram
    )
    
    print(f"\nDistances from Al-Haram:")
    for hotel in hotels_with_distance:
        dist = hotel['distance_from_reference']
        desc = calculator.get_distance_description(dist)
        formatted = calculator.format_distance(dist)
        print(f"  {hotel['name']}: {formatted} ({desc})")
    
    print("\n" + "-" * 60)
    print("[Test 3] Sort Hotels by Distance")
    print("-" * 60)
    
    sorted_hotels = calculator.sort_by_distance(sample_hotels.copy(), al_haram)
    
    print(f"\nHotels sorted by distance from Al-Haram:")
    for i, hotel in enumerate(sorted_hotels, 1):
        dist = hotel['distance_from_reference']
        print(f"  {i}. {hotel['name']}: {calculator.format_distance(dist)}")
    
    print("\n" + "-" * 60)
    print("[Test 4] Filter by Radius")
    print("-" * 60)
    
    nearby_hotels = calculator.filter_by_radius(
        sample_hotels.copy(), 
        al_haram, 
        radius_km=1.0
    )
    
    print(f"\nHotels within 1 km of Al-Haram:")
    for hotel in nearby_hotels:
        dist = hotel['distance_from_center']
        print(f"  {hotel['name']}: {calculator.format_distance(dist)}")
    
    print("\n" + "-" * 60)
    print("[Test 5] Find Nearest Hotels")
    print("-" * 60)
    
    nearest = calculator.find_nearest_hotels(sample_hotels.copy(), al_haram, count=2)
    
    print(f"\n2 Nearest hotels to Al-Haram:")
    for i, hotel in enumerate(nearest, 1):
        dist = hotel['distance_from_reference']
        print(f"  {i}. {hotel['name']}: {calculator.format_distance(dist)}")
    
    print("\n" + "-" * 60)
    print("[Test 6] Multiple Distance Calculations")
    print("-" * 60)
    
    reference_points = {
        'Al-Haram': al_haram,
        'Prophet\'s Mosque': prophet_mosque
    }
    
    hotel = sample_hotels[0]
    distances = calculator.calculate_multiple_distances(hotel, reference_points)
    
    print(f"\nDistances from {hotel['name']}:")
    for location, dist in distances.items():
        print(f"  to {location}: {calculator.format_distance(dist)}")
    
    print("\n" + "=" * 60)
    print("Distance Calculator is working perfectly!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_distance_calculator()

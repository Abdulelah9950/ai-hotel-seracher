
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.api.routes import api_bp

class TestLuxuryCount(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(api_bp, url_prefix='/api')
        self.client = self.app.test_client()
        
        # Sample hotels from schema.sql for Riyadh
        self.riyadh_hotels = [
            {
                'id': 86, 'name': 'Riyadh Marriott', 'city': 'Riyadh', 
                'star_rating': 5.0, 'price_per_night': 650.00, 
                'amenities': ["WiFi", "Pool", "Gym", "Parking", "Restaurant", "Business Center"], 
                'latitude': 24.7136, 'longitude': 46.6753
            },
            {
                'id': 87, 'name': 'Al-Faisaliah Hotel', 'city': 'Riyadh', 
                'star_rating': 5.0, 'price_per_night': 900.00, 
                'amenities': ["WiFi", "Pool", "Gym", "Parking", "Restaurant", "Spa", "Room Service"], 
                'latitude': 24.6900, 'longitude': 46.6850
            },
            {
                'id': 88, 'name': 'Riyadh Express', 'city': 'Riyadh', 
                'star_rating': 4.0, 'price_per_night': 380.00, 
                'amenities': ["WiFi", "Gym", "Parking", "Restaurant"], 
                'latitude': 24.7200, 'longitude': 46.6800
            }
        ]

    @patch('backend.api.routes.get_hotels_by_city')
    @patch('backend.api.routes.geoapify_service', None)
    @patch('backend.api.routes.get_landmark_by_name')
    def test_luxury_search_count(self, mock_landmark, mock_db_hotels):
        # Setup mocks
        mock_db_hotels.return_value = self.riyadh_hotels
        mock_landmark.return_value = None
        
        # Payload
        payload = {
            "message": "Show me luxury hotels in Riyadh",
            "user_location": {"lat": 24.0, "lng": 46.0}
        }
        
        # Make request
        print("\nSending request: 'Show me luxury hotels in Riyadh'")
        response = self.client.post('/api/chat', json=payload)
        data = response.get_json()
        
        # Check results
        hotels = data['hotels']
        print(f"\nFound {len(hotels)} hotels:")
        for h in hotels:
            print(f"- {h['name']} ({h['star_rating']} stars)")
            
        # Analyze why
        print("\nAnalysis:")
        if len(hotels) == 1:
            print("ISSUE REPRODUCED: Only 1 hotel returned.")
        elif len(hotels) == 2:
            print("Result: 2 hotels returned (5-star only). 4-star excluded.")
        elif len(hotels) == 3:
            print("Result: 3 hotels returned (All 4+ stars).")
            
if __name__ == '__main__':
    unittest.main()

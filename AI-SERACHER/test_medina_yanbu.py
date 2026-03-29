#!/usr/bin/env python3
"""Test 'hotels near me' for Medina and Yanbu"""

import requests
import json
import sys
sys.path.insert(0, 'backend')

# Medina and Yanbu coordinates
TEST_CITIES = {
    "Medina": {"lat": 24.4672, "lng": 39.6141},
    "Yanbu": {"lat": 24.1450, "lng": 38.0703},
}

print("=" * 70)
print("Testing 'hotels near me' for Medina and Yanbu")
print("=" * 70)

for city_name, location in TEST_CITIES.items():
    print(f"\n\nTesting {city_name} {location}...")
    print("-" * 70)
    
    payload = {
        "message": "hotels near me",
        "user_location": location,
        "last_search_context": {}
    }
    
    try:
        response = requests.post('http://localhost:5000/api/chat', json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"Intent: {result.get('intent')}")
            hotels = result.get('hotels', [])
            print(f"Hotels found: {len(hotels)}")
            
            if hotels:
                print(f"\nFirst 3 hotels in {city_name}:")
                for i, hotel in enumerate(hotels[:3], 1):
                    name = hotel.get('name', 'N/A')
                    rating = hotel.get('star_rating', 'N/A')
                    price = hotel.get('price_per_night', 'N/A')
                    distance = hotel.get('distance', 'N/A')
                    print(f"  {i}. {name} - Rating: {rating}*, Price: {price} SAR, Distance: {distance}m")
            else:
                print(f"No hotels found. Message: {result.get('message', 'No message')}")
        else:
            print(f"Error: Status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 70)
print("Test completed!")
print("=" * 70)

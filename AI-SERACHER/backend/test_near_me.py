#!/usr/bin/env python
import requests
import json

# Test coordinates for Medina and Yanbu
test_cases = [
    {"city": "Medina", "lat": 24.4672, "lng": 39.6028},
    {"city": "Yanbu", "lat": 24.0889, "lng": 38.0681}
]

print("=" * 70)
print("Testing 'hotels near me' for Medina and Yanbu")
print("=" * 70)

for test in test_cases:
    print(f"\nTesting: {test['city']} ({test['lat']}, {test['lng']})")
    print("-" * 70)
    
    payload = {
        "message": "hotels near me",
        "user_location": {"lat": test["lat"], "lng": test["lng"]},
        "last_search_context": {}
    }
    
    try:
        response = requests.post('http://localhost:5000/api/chat', json=payload, timeout=30)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Intent: {result.get('intent')}")
        
        hotels = result.get('hotels', [])
        print(f"Hotels found: {len(hotels)}")
        
        if hotels:
            print(f"\nTop 5 hotels in {test['city']}:")
            for i, hotel in enumerate(hotels[:5], 1):
                print(f"  {i}. {hotel.get('name', 'N/A')}")
                print(f"     Rating: {hotel.get('star_rating', 'N/A')} stars")
                print(f"     Price: {hotel.get('price_per_night', 'N/A')} SAR")
                print(f"     Distance: {hotel.get('distance_km', 'N/A')} km")
        else:
            print(f"No hotels found - Message: {result.get('message', 'No message')}")
            
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 70)
print("Testing complete!")
print("=" * 70)

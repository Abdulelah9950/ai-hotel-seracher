#!/usr/bin/env python3
"""Test the API response for 10+ hotels"""
import requests
import json
import time

time.sleep(7)  # Wait for server to be ready

try:
    response = requests.post(
        'http://127.0.0.1:5000/api/chat',
        json={
            'message': 'Show me luxury hotels in Riyadh',
            'user_location': {'lat': 24.083177250000002, 'lng': 38.040670999999996}
        },
        timeout=20
    )
    
    data = response.json()
    hotels = data.get('hotels', [])
    
    print("="*70)
    print("API RESPONSE TEST - LUXURY HOTELS")
    print("="*70)
    print(f"Total hotels returned: {len(hotels)}")
    print()
    
    if len(hotels) >= 10:
        print("✓ SUCCESS: API returns 10+ hotels as requested!")
    else:
        print(f"✗ FAILED: API only returned {len(hotels)} hotels")
    
    print()
    print("First 10 hotels:")
    for i, h in enumerate(hotels[:10]):
        name = h['name']
        rating = h.get('star_rating', 'N/A')
        print(f"{i+1:2d}. {name[:45]:45s} | ⭐ {rating}")
    
except Exception as e:
    print(f"Error: {e}")

import requests
import json

# Test the actual API response
r = requests.post('http://127.0.0.1:5000/api/chat', 
                  json={'message': 'luxury hotels in Riyadh'},
                  timeout=10)

print(f'Status: {r.status_code}')
data = r.json()
hotels = data.get('hotels', [])
print(f'Total hotels: {len(hotels)}\n')

print('Hotels returned by API:')
print('=' * 80)
for i, h in enumerate(hotels[:5], 1):
    print(f"\n{i}. {h.get('name', 'N/A')}")
    print(f"   star_rating field: {h.get('star_rating', 'MISSING')}")
    print(f"   price_per_night: {h.get('price_per_night', 'MISSING')}")
    print(f"   All keys: {list(h.keys())}")

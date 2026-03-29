import requests
import json

# Test Al-haram landmark search
r = requests.post('http://127.0.0.1:5000/api/chat', 
                  json={'message': 'I want hotels near Al-haram'})

print(f"Status: {r.status_code}")
data = r.json()
print(f"Message: {data.get('message', '')}")
print(f"Hotels found: {len(data.get('hotels', []))}")

if data.get('hotels'):
    print(f"\nFirst hotel: {data['hotels'][0].get('name', 'N/A')}")
    print(f"City: {data['hotels'][0].get('city', 'N/A')}")
    print(f"Price: {data['hotels'][0].get('price_per_night', 'N/A')} SAR")

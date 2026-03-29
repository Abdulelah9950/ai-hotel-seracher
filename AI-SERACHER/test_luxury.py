import requests
import time

print("Waiting for server to be ready...")
time.sleep(8)

# Test luxury hotels in Riyadh
r = requests.post('http://127.0.0.1:5000/api/chat', 
                  json={'message': 'Show me luxury hotels in Riyadh'},
                  timeout=10)

print(f"Status: {r.status_code}")
data = r.json()
print(f"Hotels found: {len(data.get('hotels', []))}")

if data.get('hotels'):
    print("\n=== First 10 Hotels ===")
    for i, hotel in enumerate(data['hotels'][:10]):
        print(f"{i+1:2d}. {hotel.get('star_rating', 'N/A')}⭐  {hotel.get('price_per_night', 'N/A'):>4} SAR  {hotel.get('name', 'N/A')[:45]}")

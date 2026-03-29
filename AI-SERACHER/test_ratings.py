import requests

# Test luxury hotels in Riyadh
r = requests.post('http://127.0.0.1:5000/api/chat', 
                  json={'message': 'Show me luxury hotels in Riyadh'})

data = r.json()
hotels = data.get('hotels', [])

print(f"Status: {r.status_code}")
print(f"Total hotels: {len(hotels)}")
print(f"\nFirst 10 hotels and their ratings:")
print("-" * 50)

for i, hotel in enumerate(hotels[:10]):
    rating = hotel.get('star_rating', 'N/A')
    price = hotel.get('price_per_night', 'N/A')
    name = hotel.get('name', 'N/A')[:40]
    print(f"{i+1:2d}. {rating:.1f}⭐  {price:>4} SAR  {name}")

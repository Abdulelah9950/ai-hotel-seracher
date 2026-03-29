import requests
import json

# Test what Geoapify actually returns
r = requests.post('http://127.0.0.1:5000/api/chat', 
                  json={'message': 'Show me luxury hotels in Riyadh'})

data = r.json()
hotels = data.get('hotels', [])

print(f"Total hotels: {len(hotels)}")
print(f"\nAll 15 hotels with ratings:")
print("-" * 60)

for i, hotel in enumerate(hotels):
    rating = hotel.get('star_rating', 'N/A')
    price = hotel.get('price_per_night', 'N/A')
    name = hotel.get('name', 'N/A')[:35]
    print(f"{i+1:2d}. {rating}⭐  {price:>4} SAR  {name}")

# Check if they're actually filtered
print(f"\n\nHotels with 4+ stars: {len([h for h in hotels if h.get('star_rating', 0) >= 4.0])}")
print(f"Hotels with 3-3.5 stars: {len([h for h in hotels if 3.0 <= h.get('star_rating', 0) < 4.0])}")
print(f"Hotels with <3 stars: {len([h for h in hotels if h.get('star_rating', 0) < 3.0])}")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.geoapify_service import GeoapifyService
import json

geo = GeoapifyService()

# Try to get raw Geoapify response
results = geo.search_hotels_nearby((24.7136, 46.6753), radius=5000, limit=5)

print("First 3 hotels with all available data:")
print("=" * 80)

for i, hotel in enumerate(results[:3], 1):
    print(f"\n{i}. {hotel['name']}")
    print(f"   Rating: {hotel.get('rating')}")
    print(f"   Datasource: {hotel.get('datasource')}")

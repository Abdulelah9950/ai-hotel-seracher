from geoapify_service import GeoapifyService
import json

geo = GeoapifyService()
results = geo.search_hotels_nearby("24.7136, 46.6753", radius=5000, keyword="hotel", limit=20)

print("Raw Geoapify response (first 5 hotels):")
print(json.dumps(results[:5], indent=2, ensure_ascii=False))

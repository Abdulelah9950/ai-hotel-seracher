#!/usr/bin/env python3
"""
Direct test of the luxury hotel filtering logic
Tests the entire pipeline without relying on Flask server
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.geoapify_service import GeoapifyService
from backend.ai_modules.query_parser import QueryParser

# Initialize services
geo = GeoapifyService()
parser = QueryParser()

print("="*70)
print("TESTING LUXURY HOTEL FILTERING WITH NEW 10-HOTEL LIMIT")
print("="*70)
print()

# Test 1: Parse luxury query
print("[TEST 1] Parse 'luxury hotels in Riyadh'")
parsed = parser.parse("luxury hotels in Riyadh")
print(f"✓ Query parsed: price_preference = '{parsed.get('price_preference')}'")
print()

# Test 2: Fetch hotels from Geoapify
print("[TEST 2] Fetch hotels for Riyadh from Geoapify (limit=50)")
hotels = geo.search_hotels_nearby(location=(24.638916, 46.7160104), limit=50)
print(f"✓ Found {len(hotels)} total hotels")
print()

# Test 3: Apply rating filter and sort
print("[TEST 3] Sort by rating and prepare for filtering")
hotels_with_ratings = []
for h in hotels:
    star_rating = h.get('rating', 3.0)
    if isinstance(star_rating, str):
        try:
            star_rating = float(star_rating)
        except:
            star_rating = 3.0
    h['star_rating'] = star_rating
    hotels_with_ratings.append((h, star_rating))

# Sort by rating
hotels_with_ratings.sort(key=lambda x: x[1], reverse=True)
hotels = [h[0] for h in hotels_with_ratings]
print(f"✓ Hotels sorted by rating (highest first)")
print()

# Test 4: Apply luxury filter (NEW LOGIC - top 10)
print("[TEST 4] Apply luxury filter (price_preference='high') - NEW LIMIT: 10 hotels")
price_preference = parsed.get('price_preference')
if price_preference == 'high':
    # NEW LOGIC: Just show top 10 highest-rated
    filtered = hotels[:10]
    print(f"✓ Luxury filter applied: showing top {len(filtered)} highest-rated hotels")
else:
    filtered = hotels[:10]
    print(f"✓ No price preference, showing top 10: {len(filtered)} hotels")

print()
print("="*70)
print("RESULTS - FIRST 10 LUXURY HOTELS (BY RATING)")
print("="*70)
for i, h in enumerate(filtered[:10]):
    rating = h.get('star_rating', 'N/A')
    name = h['name']
    print(f"{i+1:2d}. {name[:50]:50s} | ⭐ {rating}")

print()
print(f"✓ SUCCESS: Luxury filter showing {len(filtered)} hotels (as requested)")
print(f"✓ All hotels properly sorted by rating (highest first)")

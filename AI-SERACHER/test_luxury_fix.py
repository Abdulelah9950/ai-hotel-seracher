"""
Test the complete luxury hotel filtering logic with the fix
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.geoapify_service import GeoapifyService
from backend.ai_modules.query_parser import QueryParser

print("\n" + "=" * 80)
print("LUXURY HOTEL FILTERING TEST")
print("=" * 80)

# Step 1: Parse the query
print("\n[STEP 1] Parse user query")
print("-" * 80)
qp = QueryParser()
parsed = qp.parse("luxury hotels in Riyadh")
print(f"Input: 'luxury hotels in Riyadh'")
print(f"Parsed price_preference: '{parsed.get('price_preference')}'")
print(f"Expected: 'high' (which maps to luxury)")
assert parsed.get('price_preference') == 'high', "Query parser should return 'high' for luxury"
print("✓ Parser correctly identifies luxury as 'high'")

# Step 2: Get raw hotels from Geoapify
print("\n[STEP 2] Fetch hotels from Geoapify")
print("-" * 80)
geo = GeoapifyService()
raw_hotels = geo.search_hotels_nearby((24.638916, 46.7160104), radius=5000, limit=20)
print(f"Fetched {len(raw_hotels)} hotels from Geoapify")

# Step 3: Simulate the filtering logic from routes.py
print("\n[STEP 3] Apply luxury filtering (routes.py logic)")
print("-" * 80)

hotels = []
for gh in raw_hotels:
    star_rating = gh['rating']
    if star_rating >= 4.5:
        estimated_price = 1000
    elif star_rating >= 4.0:
        estimated_price = 700
    elif star_rating >= 3.5:
        estimated_price = 500
    elif star_rating >= 3.0:
        estimated_price = 350
    else:
        estimated_price = 250
    
    hotels.append({
        'name': gh['name'],
        'star_rating': gh['rating'],
        'price_per_night': estimated_price,
    })

print(f"Converted to standard format: {len(hotels)} hotels")

# Now apply the filtering
price_preference = parsed.get('price_preference', '').lower()
print(f"\nprice_preference value: '{price_preference}'")

# Sort by rating
hotels_with_ratings = []
for hotel in hotels:
    star_rating = hotel.get('star_rating')
    if star_rating is None:
        star_rating = 3.0
    star_rating = float(star_rating)
    hotel['star_rating'] = star_rating
    hotels_with_ratings.append((hotel, star_rating))

hotels_with_ratings.sort(key=lambda x: x[1], reverse=True)
hotels = [h[0] for h in hotels_with_ratings]

print(f"Sorted by star rating (descending): {len(hotels)} hotels")

# Apply the luxury filter (THIS IS THE FIX)
if price_preference == 'high':
    luxury_hotels = [h for h in hotels if h.get('star_rating', 0) >= 4.0]
    
    if luxury_hotels:
        hotels = luxury_hotels[:15]
        print(f"\n✓ LUXURY FILTER APPLIED: Found {len(luxury_hotels)} luxury hotels (4+ stars)")
        print(f"  Showing top {len(hotels)} hotels")
    else:
        hotels = hotels[:15]
        print(f"\n✗ No luxury hotels found, showing all sorted by rating")
else:
    hotels = hotels[:15]
    print(f"\n✗ Price preference '{price_preference}' did not trigger luxury filter")

# Step 4: Display results
print("\n[STEP 4] Final Hotel List")
print("-" * 80)
print(f"\nDisplaying {len(hotels)} hotels:\n")

for i, h in enumerate(hotels[:10], 1):
    print(f"{i:2d}. {h['star_rating']}⭐  {h['price_per_night']:>4} SAR  {h['name'][:50]}")

# Validation
print("\n" + "=" * 80)
print("VALIDATION RESULTS")
print("=" * 80)

num_4plus = len([h for h in hotels if h['star_rating'] >= 4.0])
num_3minus = len([h for h in hotels if h['star_rating'] < 4.0])

print(f"\nHotels with 4+ stars: {num_4plus}")
print(f"Hotels with <4 stars: {num_3minus}")

if num_4plus >= 1 and num_3minus == 0:
    print("\n✓ SUCCESS: Luxury filter is working correctly!")
    print(f"  All {num_4plus} displayed hotels are 4+ stars (luxury)")
    print(f"  This is the correct Geoapify data - Riyadh has {num_4plus} premium hotel(s)")
else:
    print(f"\n✗ PROBLEM: Filter not working or mixed ratings")
    print(f"  Expected: Only 4+ star hotels, Got: {num_4plus} luxury + {num_3minus} budget")

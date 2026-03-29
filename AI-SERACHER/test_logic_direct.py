#!/usr/bin/env python
"""
Test the luxury hotel filtering logic directly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.geoapify_service import GeoapifyService

# Get raw hotels data
geo = GeoapifyService()
raw_hotels = geo.search_hotels_nearby((24.7136, 46.6753), radius=5000, limit=20)

print("=" * 80)
print("RAW GEOAPIFY RESPONSE - Riyadh Hotels")
print("=" * 80)
print(f"Total raw hotels: {len(raw_hotels)}\n")

# Convert to our format (simulating what app does)
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
    
    hotel = {
        'name': gh['name'],
        'address': gh['address'],
        'city': gh['city'],
        'latitude': gh['latitude'],
        'longitude': gh['longitude'],
        'star_rating': gh['rating'],
        'price_per_night': estimated_price,
        'rating_raw': gh.get('rating', 3.0),
    }
    hotels.append(hotel)

print("\nALL HOTELS (sorted by star_rating descending):")
print("-" * 80)

# Apply the EXACT logic from routes.py
price_preference = 'luxury'
min_rating = 0

# Step 1: Sort by rating descending
hotels_with_ratings = []
for hotel in hotels:
    star_rating = hotel.get('star_rating')
    if star_rating is None:
        star_rating = 3.0
    star_rating = float(star_rating)
    hotel['star_rating'] = star_rating
    hotels_with_ratings.append((hotel, star_rating))

# Sort by rating (highest first)
hotels_with_ratings.sort(key=lambda x: x[1], reverse=True)
hotels = [h[0] for h in hotels_with_ratings]

# Step 2: Filter by minimum rating
if min_rating > 0:
    hotels = [h for h in hotels if h.get('star_rating', 3.0) >= min_rating]

# Step 3: Apply price preference filter
if price_preference == 'luxury':
    luxury_hotels = [h for h in hotels if h.get('star_rating', 0) >= 4.0]
    
    if luxury_hotels:
        hotels = luxury_hotels[:15]
        print(f"Found {len(luxury_hotels)} luxury hotels (4+ stars)")
    else:
        print(f"No luxury hotels (4+ stars) found, showing all hotels sorted by rating")
        hotels = hotels[:15]

print(f"\nTotal hotels shown: {len(hotels)}\n")
for i, h in enumerate(hotels, 1):
    print(f"{i:2d}. {h['star_rating']}⭐  {h['price_per_night']:>4} SAR  {h['name'][:50]}")

print("\n" + "=" * 80)
print(f"Hotels with 4+ stars: {len([h for h in hotels if h['star_rating'] >= 4.0])}")
print(f"Hotels with 3-3.5 stars: {len([h for h in hotels if 3.0 <= h['star_rating'] < 4.0])}")

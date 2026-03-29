# Google Places API Integration Guide

## Overview

This guide will help you integrate Google Places API to fetch real hotels with live data instead of using the static database.

## Step 1: Get Google Maps API Key

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "Hotel Booking AI")
4. Click "Create"

### 1.2 Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for and enable these APIs:
   - **Places API (New)** - For searching hotels
   - **Geocoding API** - For address to coordinates conversion
   - **Distance Matrix API** - For calculating distances
   - **Maps JavaScript API** (optional) - For better map visualization

### 1.3 Create API Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. Copy your API key (looks like: `AIzaSyB...`)
4. Click "Restrict Key" (recommended for security):
   - Set Application restrictions (HTTP referrers for web, or IP addresses for backend)
   - Set API restrictions to only the APIs you enabled above

### 1.4 Set Up Billing (Required!)

⚠️ **Important**: Google Maps APIs require a billing account even though they offer free tier.

- Free tier: $200 credit per month
- Places API: $17 per 1000 requests after free tier
- Distance Matrix API: $5-10 per 1000 elements
- Most student projects will stay within free tier!

1. Go to "Billing" in Google Cloud Console
2. Link a credit card (you won't be charged unless you exceed free tier)
3. Set up budget alerts (recommended: $50/month)

## Step 2: Configure Your Project

### 2.1 Create .env File

```bash
cd backend
cp .env.example .env
```

### 2.2 Add Your API Key

Edit `.env` file:

```
GOOGLE_MAPS_API_KEY=AIzaSyB...YOUR_ACTUAL_KEY_HERE
```

## Step 3: Test the Integration

Run the test script:

```bash
cd backend
python services/google_places.py
```

If successful, you should see real hotels near Al-Haram!

## Step 4: Update Database with Real Hotels (Optional)

You can populate your database with real hotels from Google:

```python
from services.google_places import GooglePlacesService
from database.db_connection import add_hotel

service = GooglePlacesService()

# Search Makkah hotels
makkah_hotels = service.search_hotels_nearby((21.4225, 39.8262), radius=5000)

# Add to database
for hotel in makkah_hotels:
    add_hotel({
        'name': hotel['name'],
        'address': hotel['address'],
        'city': 'Makkah',
        'latitude': hotel['latitude'],
        'longitude': hotel['longitude'],
        'star_rating': hotel['rating'],  # Google rating
        'google_place_id': hotel['google_place_id']
    })
```

## Step 5: Modify Chat Endpoint

Update `backend/api/routes.py` to use Google Places:

```python
from services.google_places import GooglePlacesService

google_service = GooglePlacesService()

# In /api/chat endpoint, replace database search with:
if parsed_query.get('landmark'):
    # Get landmark coordinates
    location = (landmark['latitude'], landmark['longitude'])

    # Search Google Places
    hotels = google_service.search_hotels_nearby(
        location=location,
        radius=5000,
        keyword=parsed_query.get('price_preference')
    )
```

## Cost Estimation

For a student project with 1000 queries/month:

- Places Nearby Search: 1000 requests × $0.032 = $32
- Place Details: 1000 requests × $0.017 = $17
- **Total: $49/month**
- **Free tier covers: $200/month**
- **You pay: $0** (within free tier!)

## Troubleshooting

### Error: "This API project is not authorized to use this API"

- Make sure you enabled the specific API in Google Cloud Console
- Wait 5 minutes after enabling (propagation time)

### Error: "REQUEST_DENIED"

- Check if billing is enabled
- Verify API key is correct in .env file
- Make sure API key restrictions allow your app

### Error: "OVER_QUERY_LIMIT"

- You exceeded free tier
- Check billing account
- Reduce number of requests

## Alternative: Hybrid Approach

You can use BOTH database and Google Places:

1. Use database for demo/offline testing
2. Fallback to Google Places for cities not in database
3. Cache Google Places results in database

## Security Best Practices

1. **Never commit .env file to git**
2. Add API key restrictions in Google Console
3. Set spending limits in billing
4. Use environment variables, not hardcoded keys
5. Rotate API keys periodically

## Next Steps

Once you have your API key:

1. Test with `python services/google_places.py`
2. Integrate into chat endpoint
3. Update frontend to show real hotel photos
4. Add Google Maps instead of Leaflet (optional)

---

**Need Help?**

- [Google Places API Documentation](https://developers.google.com/maps/documentation/places/web-service/overview)
- [Python Client Library](https://github.com/googlemaps/google-maps-services-python)
- Contact: Your team members for support!

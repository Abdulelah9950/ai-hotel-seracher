# Test the Flask API
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("\n" + "=" * 60)
print("Testing Hotel Booking AI API")
print("=" * 60)

# Test 1: Health Check
print("\n[Test 1] Health Check")
print("-" * 60)
response = requests.get(f"{BASE_URL}/api/health")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 2: Chat - Search for hotels
print("\n" + "-" * 60)
print("[Test 2] Chat - Find cheap hotels near Al-Haram with WiFi")
print("-" * 60)

chat_data = {
    "message": "Find me a cheap hotel near Al-Haram with WiFi"
}

response = requests.post(
    f"{BASE_URL}/api/chat",
    json=chat_data,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
result = response.json()

print(f"\nIntent: {result.get('intent')}")
print(f"Message: {result.get('message')}")
print(f"\nLandmark: {result.get('landmark', {}).get('name')}")
print(f"Total hotels found: {result.get('total_found')}")

print(f"\nTop Recommendations:")
for i, hotel in enumerate(result.get('hotels', []), 1):
    print(f"\n  {i}. {hotel['name']}")
    print(f"     Score: {hotel['recommendation_score']}/100")
    print(f"     Price: {hotel['price_per_night']} SAR")
    print(f"     Rating: {hotel['star_rating']} stars")
    print(f"     Distance: {hotel.get('distance', 'N/A')}")
    print(f"     {hotel['explanation']}")

# Test 3: Get specific hotel details
print("\n" + "-" * 60)
print("[Test 3] Get Hotel Details with Sentiment Analysis")
print("-" * 60)

response = requests.get(f"{BASE_URL}/api/hotels/1")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    hotel = result['hotel']
    print(f"\nHotel: {hotel['name']}")
    print(f"City: {hotel['city']}")
    print(f"Rating: {hotel['star_rating']} stars")
    print(f"Price: {hotel['price_per_night']} SAR/night")
    print(f"Reviews: {result['review_count']}")
    
    if result.get('sentiment_analysis'):
        sentiment = result['sentiment_analysis']
        print(f"\nSentiment Analysis:")
        print(f"  Average Polarity: {sentiment['average_polarity']:.2f}")
        print(f"  Positive: {sentiment['distribution']['positive']}%")
        print(f"  Neutral: {sentiment['distribution']['neutral']}%")
        print(f"  Negative: {sentiment['distribution']['negative']}%")
    
    print(f"\nSummary: {result['review_summary']}")

# Test 4: Nearby hotels
print("\n" + "-" * 60)
print("[Test 4] Find Hotels Near Al-Haram (within 2 km)")
print("-" * 60)

nearby_data = {
    "latitude": 21.4225,
    "longitude": 39.8262,
    "radius_km": 2,
    "count": 5
}

response = requests.post(
    f"{BASE_URL}/api/hotels/nearby",
    json=nearby_data,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
result = response.json()

print(f"\nFound {result['count']} hotels within {result['search_radius']}")
for i, hotel in enumerate(result.get('hotels', []), 1):
    print(f"  {i}. {hotel['name']} - {hotel.get('distance_formatted', 'N/A')}")

# Test 5: Get all landmarks
print("\n" + "-" * 60)
print("[Test 5] Get All Landmarks")
print("-" * 60)

response = requests.get(f"{BASE_URL}/api/landmarks")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\nTotal landmarks: {result['count']}")
    for landmark in result.get('landmarks', [])[:5]:  # Show first 5
        print(f"  - {landmark['name']} ({landmark['city']})")

print("\n" + "=" * 60)
print("All API Tests Completed!")
print("=" * 60 + "\n")

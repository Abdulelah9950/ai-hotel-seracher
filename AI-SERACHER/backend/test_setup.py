# Test Script - Verify Setup
# This script tests database connection and AI libraries

print("=" * 50)
print("Testing AI Hotel Booking Setup")
print("=" * 50)

# Test 1: Database Connection
print("\n[Test 1] Testing MySQL Database Connection...")
try:
    import mysql.connector
    
    # Connect to database
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Modtha@7',  # ← UPDATE THIS with your MySQL password
        database='hotel_booking_ai'
    )
    
    cursor = db.cursor()
    
    # Test query - count hotels
    cursor.execute("SELECT COUNT(*) FROM hotels")
    hotel_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM reviews")
    review_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM landmarks")
    landmark_count = cursor.fetchone()[0]
    
    print(f"✓ Database connected successfully!")
    print(f"  - Hotels: {hotel_count}")
    print(f"  - Reviews: {review_count}")
    print(f"  - Landmarks: {landmark_count}")
    
    # Test query - get a sample hotel
    cursor.execute("SELECT name, city, price_per_night FROM hotels LIMIT 1")
    sample = cursor.fetchone()
    print(f"  - Sample hotel: {sample[0]} in {sample[1]} ({sample[2]} SAR/night)")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    print("  Please check your MySQL password in this file (line 13)")

# Test 2: TextBlob (Sentiment Analysis)
print("\n[Test 2] Testing TextBlob (Sentiment Analysis)...")
try:
    from textblob import TextBlob
    
    # Test sentiment analysis
    text = "The hotel was amazing! Very clean and great location."
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    
    print(f"✓ TextBlob is working!")
    print(f"  - Sample text: '{text}'")
    print(f"  - Sentiment score: {sentiment:.2f} (positive)")
    
except Exception as e:
    print(f"✗ TextBlob failed: {e}")

# Test 3: FuzzyWuzzy (Fuzzy String Matching)
print("\n[Test 3] Testing FuzzyWuzzy (Fuzzy String Matching)...")
try:
    from fuzzywuzzy import fuzz
    
    # Test fuzzy matching
    user_input = "alharam"
    database_value = "Al-Haram Al-Makki"
    similarity = fuzz.ratio(user_input.lower(), database_value.lower())
    
    print(f"✓ FuzzyWuzzy is working!")
    print(f"  - User typed: '{user_input}'")
    print(f"  - Database has: '{database_value}'")
    print(f"  - Match similarity: {similarity}%")
    
except Exception as e:
    print(f"✗ FuzzyWuzzy failed: {e}")

# Test 4: Geopy (Distance Calculation)
print("\n[Test 4] Testing Geopy (Distance Calculation)...")
try:
    from geopy.distance import geodesic
    
    # Test distance calculation
    al_haram = (21.4225, 39.8262)  # Al-Haram coordinates
    sample_hotel = (21.4244, 39.8267)  # Sample hotel coordinates
    
    distance = geodesic(al_haram, sample_hotel).km
    
    print(f"✓ Geopy is working!")
    print(f"  - From: Al-Haram Al-Makki")
    print(f"  - To: Sample Hotel")
    print(f"  - Distance: {distance:.2f} km")
    
except Exception as e:
    print(f"✗ Geopy failed: {e}")

# Test 5: Pandas (Data Processing)
print("\n[Test 5] Testing Pandas (Data Processing)...")
try:
    import pandas as pd
    
    # Create sample data
    data = {
        'hotel': ['Hotel A', 'Hotel B', 'Hotel C'],
        'price': [400, 600, 300],
        'rating': [4.5, 4.8, 4.2]
    }
    
    df = pd.DataFrame(data)
    cheap_hotels = df[df['price'] < 500]
    
    print(f"✓ Pandas is working!")
    print(f"  - Total hotels: {len(df)}")
    print(f"  - Hotels under 500 SAR: {len(cheap_hotels)}")
    
except Exception as e:
    print(f"✗ Pandas failed: {e}")

# Test 6: Flask
print("\n[Test 6] Testing Flask...")
try:
    from flask import Flask
    
    app = Flask(__name__)
    
    print(f"✓ Flask is working!")
    print(f"  - Flask version: {Flask.__version__}")
    
except Exception as e:
    print(f"✗ Flask failed: {e}")

# Test 7: Requests (for Google Maps API)
print("\n[Test 7] Testing Requests (HTTP Library)...")
try:
    import requests
    
    print(f"✓ Requests is working!")
    print(f"  - Ready for Google Maps API calls")
    
except Exception as e:
    print(f"✗ Requests failed: {e}")

# Summary
print("\n" + "=" * 50)
print("SETUP VERIFICATION COMPLETE")
print("=" * 50)
print("\n✓ If all tests passed, you're ready to build the backend!")
print("✗ If any test failed, please install the missing package or fix the issue.")
print("\nNext step: Build Flask backend with AI modules")
print("=" * 50)

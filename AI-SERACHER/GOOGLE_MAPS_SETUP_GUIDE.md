# How to Fetch Hotels from Google Maps and Store in Database

## 📋 Overview

This guide explains how to use Google Maps Places API to fetch real hotel data and store it in your MySQL database. This will give you access to hundreds of real hotels with accurate information.

---

## 🔑 Step 1: Get Google Maps API Key

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: "Hotel Booking AI"
4. Click "Create"

### 1.2 Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search and enable these APIs:
   - ✅ **Places API** (for searching hotels)
   - ✅ **Geocoding API** (for address conversions)
   - ✅ **Maps JavaScript API** (for frontend map display)

### 1.3 Create API Key

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. Copy your API key (looks like: `AIzaSyD1234567890abcdefghijklmnop`)
4. Click "Restrict Key" (recommended for security):
   - **API restrictions**: Select the 3 APIs you enabled above
   - **Application restrictions**: Choose based on your needs (HTTP referrers for web)
5. Click "Save"

### 1.4 API Pricing (Important!)

**Free Tier:**

- Google provides **$200 free credit per month**
- Places API costs: **$0.017 per request**
- With free credit: **~11,000 requests/month free**

**Cost Estimate for This Project:**

- Each city search: ~3 requests (60 hotels max)
- 4 cities = 12 requests = **~$0.20**
- Well within free tier! ✅

**Recommendation:** Fetch hotels once, store in database, update monthly

---

## 🛠️ Step 2: Install Required Packages

Open your terminal in the project directory and run:

```powershell
# Install required Python packages
pip install requests mysql-connector-python
```

**What these packages do:**

- `requests`: Makes HTTP requests to Google Maps API
- `mysql-connector-python`: Connects Python to MySQL database

---

## 🗄️ Step 3: Set Up MySQL Database

### 3.1 Install MySQL (if not already installed)

**Download MySQL:**

- Go to [MySQL Downloads](https://dev.mysql.com/downloads/installer/)
- Download MySQL Installer for Windows
- Run installer and choose "Developer Default"
- Set root password during installation (remember this!)

### 3.2 Create Database

**Option A: Using MySQL Workbench (GUI)**

1. Open MySQL Workbench
2. Connect to your local MySQL server
3. Click "File" → "Open SQL Script"
4. Select `database/schema.sql`
5. Click Execute (⚡ icon)

**Option B: Using Command Line**

```powershell
# Navigate to database folder
cd database

# Run SQL script
mysql -u root -p < schema.sql

# Enter your MySQL password when prompted
```

---

## ⚙️ Step 4: Configure the Script

Open `backend/utils/fetch_hotels_from_google.py` and update:

### 4.1 Add Your API Key (Line 42)

```python
# Replace with your actual Google Maps API key
GOOGLE_API_KEY = "AIzaSyD1234567890abcdefghijklmnop"  # ← Paste your key here
```

### 4.2 Update Database Credentials (Lines 45-50)

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',              # Your MySQL username
    'password': 'your_password', # Your MySQL password ← Change this
    'database': 'hotel_booking_ai'
}
```

### 4.3 (Optional) Customize Cities and Search Radius

```python
CITIES = [
    {
        'name': 'Makkah',
        'lat': 21.4225,
        'lng': 39.8262,
        'radius': 10000  # 10km radius - adjust if needed
    },
    # Add more cities if you want
]
```

---

## 🚀 Step 5: Run the Script

### 5.1 Navigate to Backend Utils Folder

```powershell
cd backend/utils
```

### 5.2 Run the Script

```powershell
python fetch_hotels_from_google.py
```

### 5.3 What You'll See

```
==================================================
GOOGLE MAPS HOTEL FETCHER
==================================================

This script will fetch hotels from Google Maps Places API
and store them in your MySQL database.

Do you want to continue? (yes/no): yes

✓ Connected to database

==================================================
Searching for hotels in Makkah
==================================================
Fetched 20 hotels (Total: 20)
Fetched 20 hotels (Total: 40)
Fetched 15 hotels (Total: 55)
Found 55 hotels in Makkah

✓ Inserted: Makkah Clock Royal Tower (ID: 19)
✓ Inserted: Swissotel Makkah (ID: 20)
✓ Inserted: Dar Al Tawhid InterContinental (ID: 21)
...

==================================================
SUMMARY
==================================================
✓ New hotels inserted: 180
• Hotels already in database: 18
Total hotels: 198
```

---

## 📊 Step 6: Verify Data in Database

### Check Inserted Hotels

```sql
-- Open MySQL and run:
USE hotel_booking_ai;

-- Count total hotels
SELECT COUNT(*) as total_hotels FROM hotels;

-- View hotels by city
SELECT city, COUNT(*) as hotel_count
FROM hotels
GROUP BY city;

-- View sample hotels from Google
SELECT name, city, price_per_night, star_rating, google_place_id
FROM hotels
WHERE google_place_id IS NOT NULL
LIMIT 10;
```

---

## 🔄 How the Script Works

### 1. **Search for Hotels**

```
Google Places API → Search "lodging" near coordinates
                 → Returns up to 60 results per location
```

### 2. **Parse Hotel Data**

```
Raw Google Data → Extract: name, address, coordinates
                → Convert: price_level to SAR
                → Map: types to amenities
```

### 3. **Store in Database**

```
Parsed Data → Check if hotel exists (by place_id)
           → Insert new hotels
           → Skip duplicates
```

### 4. **Data Mapping**

**Google Price Level → SAR Price:**

- Level 0 (Free) → 150 SAR
- Level 1 (Inexpensive) → 250 SAR
- Level 2 (Moderate) → 450 SAR
- Level 3 (Expensive) → 750 SAR
- Level 4 (Very Expensive) → 1200 SAR

**Google Types → Amenities:**

- `swimming_pool` → Pool
- `parking` → Parking
- `gym` → Gym
- `spa` → Spa
- `restaurant` → Restaurant

---

## 💡 Advanced Usage

### Fetch Hotel Reviews from Google

The script includes a function to fetch reviews:

```python
def fetch_hotel_reviews_from_google(place_id):
    """Get reviews for a specific hotel"""
    details = get_place_details(place_id)
    reviews = details.get('reviews', [])
    return reviews
```

**To use it:**

1. Get a hotel's `google_place_id` from database
2. Call the function with that ID
3. Process and store reviews in `reviews` table
4. Use your sentiment analyzer to calculate `sentiment_score`

### Update Hotel Data Periodically

Create a scheduled task to update hotel information:

```python
# Run monthly to refresh prices and ratings
def update_existing_hotels():
    # Fetch all hotels with google_place_id
    # Get updated details from Google
    # Update database records
```

---

## ⚠️ Important Notes

### 1. **API Rate Limits**

- Script includes `time.sleep(0.1)` to avoid rate limiting
- Don't remove delays or you may get blocked

### 2. **Duplicate Prevention**

- Script checks `google_place_id` before inserting
- Re-running script won't create duplicates ✅

### 3. **Cost Management**

- **Run once** to populate database
- Update **monthly** instead of real-time
- Monitor usage in [Google Cloud Console](https://console.cloud.google.com/)

### 4. **Data Accuracy**

- Google's price levels are approximate
- You may want to verify/adjust prices manually
- Star ratings are based on user reviews

### 5. **Alternative Approaches**

**Option A: One-time Fetch (Recommended)**

- Run script once to get hotels
- Store in database
- Update occasionally

**Option B: Hybrid Approach**

- Use database for main searches
- Call Google API for real-time updates when needed
- Best balance of cost and accuracy

**Option C: Real-time API**

- Query Google Maps on every search
- Most accurate but expensive
- Not recommended for this project

---

## 🐛 Troubleshooting

### Error: "API key not valid"

- Check if API key is correct
- Make sure Places API is enabled
- Check API restrictions in Google Cloud Console

### Error: "Database connection failed"

- Verify MySQL is running
- Check username and password in `DB_CONFIG`
- Confirm database `hotel_booking_ai` exists

### Error: "OVER_QUERY_LIMIT"

- You've exceeded free tier
- Check usage in Google Cloud Console
- Wait for monthly reset or add billing

### Error: "REQUEST_DENIED"

- API not enabled in Google Cloud
- Go enable Places API

### No hotels found

- Check coordinates are correct
- Increase search radius
- Try different cities

---

## 📝 Summary

✅ **What You Get:**

- 50-200 real hotels per city
- Accurate GPS coordinates
- Real ratings from Google users
- Approximate pricing
- Amenities information

✅ **Benefits:**

- Real data instead of fake/sample data
- Accurate distances for your map feature
- Professional demo with real hotels
- Easy to expand to more cities

✅ **Cost:**

- **FREE** for this project (within Google's free tier)
- One-time fetch = ~$0.20 worth of API calls

---

## 🎯 Next Steps

After populating your database:

1. ✅ You now have real hotel data
2. ✅ Ready to build Flask backend
3. ✅ Can implement AI query parser
4. ✅ Can test distance calculations with real coordinates
5. ✅ Can display hotels on Google Maps

Your database is now production-ready! 🚀

# Geoapify Integration Guide

## Why Geoapify Instead of Google Places?

✅ **FREE TIER**: 3,000 requests/day with no credit card  
✅ **NO BILLING REQUIRED**: Just sign up with email  
✅ **SAME FUNCTIONALITY**: Search hotels, geocoding, places API  
✅ **WORKS IN SAUDI ARABIA**: No regional restrictions

**Google Places is kept** in the codebase to show architectural knowledge!

---

## Step 1: Get Your FREE API Key (2 minutes)

### 1.1 Sign Up

1. Go to: **https://www.geoapify.com/**
2. Click **"Get Started Free"** or **"Sign Up"**
3. Enter your email and create password
4. Verify your email (check inbox/spam)

### 1.2 Get API Key

1. Log in to Geoapify
2. Go to **"My Projects"**
3. Click on your default project
4. Go to **"API Keys"** tab
5. **Copy your API key** (looks like: `abc123def456ghi789...`)

---

## Step 2: Configure Your Project (1 minute)

### 2.1 Create .env File

```bash
cd backend
cp .env.example .env
```

### 2.2 Add Your API Key

Open `backend/.env` and add your key:

```bash
GEOAPIFY_API_KEY=abc123def456ghi789...YOUR_ACTUAL_KEY
```

**Important:** Replace `YOUR_ACTUAL_KEY` with the key you copied!

---

## Step 3: Test the Integration (1 minute)

Run the test script:

```bash
cd backend
python services/geoapify_service.py
```

**Expected output:**

```
🧪 Testing Geoapify Service
============================================================

📍 Test 1: Hotels near Al-Haram, Makkah
------------------------------------------------------------
✅ Found 5 hotels near (21.4225, 39.8262)

1. Hilton Makkah Convention Hotel
   📍 Jabal Omar, Makkah, Saudi Arabia
   ⭐ Rating: 4.5
   📞 +966-12-123-4567
   🌐 www.hilton.com

2. Swissôtel Makkah
   ...

✅ All tests completed!
```

If you see hotels, **it's working!** 🎉

---

## Step 4: Update Chat Endpoint (2 minutes)

We'll modify `backend/api/routes.py` to use Geoapify for real hotel searches.

**What changes:**

- Search real hotels from Geoapify API
- Calculate distances using your existing DistanceCalculator
- Still use AI modules for recommendations
- Fallback to database if API fails

---

## Step 5: Test in Your Chatbot

Once integrated, test with queries like:

- "Hotels near Al-Haram"
- "Luxury hotels in Riyadh"
- "Budget hotels near Prophet's Mosque"

You'll get **real hotels** with:

- ✅ Real names and addresses
- ✅ Actual GPS coordinates
- ✅ Live ratings
- ✅ Phone numbers and websites
- ✅ Accurate distances

---

## Features Comparison

| Feature        | Database (Current)              | Geoapify (New)                  |
| -------------- | ------------------------------- | ------------------------------- |
| Hotel count    | 34 hotels                       | Thousands of real hotels        |
| Data freshness | Static                          | Real-time                       |
| Coverage       | Makkah, Madinah, Riyadh, Jeddah | Entire Saudi Arabia + World     |
| Ratings        | Manual entry                    | Real Google/TripAdvisor ratings |
| Amenities      | JSON array                      | Real amenities                  |
| Photos         | None                            | Available via API               |
| Cost           | Free                            | 3000 requests/day FREE          |
| Setup          | Done ✅                         | 2 minutes                       |

---

## API Limits

**Free Tier:**

- 3,000 requests per day
- ~1 request per hotel search
- Perfect for student projects!

**If you exceed:**

- API returns error
- System falls back to database
- No charges, no problem!

---

## Troubleshooting

### Error: "API key is required"

- Check `.env` file has `GEOAPIFY_API_KEY=...`
- Make sure no extra spaces
- Restart Flask server after adding key

### Error: "403 Forbidden"

- API key might be invalid
- Copy key again from Geoapify dashboard
- Check for typos

### Error: "Connection timeout"

- Check internet connection
- Geoapify servers might be slow
- System will fallback to database

---

## Next Steps

1. ✅ Sign up for Geoapify
2. ✅ Get API key
3. ✅ Add to `.env` file
4. ✅ Test with `python services/geoapify_service.py`
5. ⏳ We'll integrate into chat endpoint
6. ⏳ Test in chatbot UI

---

## Why Keep Google Places Code?

**In your demo/report, you can say:**

> "We designed a service layer abstraction that supports multiple map providers. We implemented both Google Places API and Geoapify. Google Places offers premium features but requires billing setup, while Geoapify provides a generous free tier perfect for development. The modular architecture allows switching between providers with a single line change."

**This shows:**

- 🎯 Enterprise architecture thinking
- 🎯 API abstraction patterns
- 🎯 Fallback strategies
- 🎯 Cost optimization

---

## Security Notes

- ✅ API key is in `.env` (not committed to git)
- ✅ `.gitignore` excludes `.env`
- ✅ Frontend doesn't expose API key (server-side only)
- ✅ Free tier limits prevent cost overruns

---

**Ready?** Get your API key and let's test it! 🚀

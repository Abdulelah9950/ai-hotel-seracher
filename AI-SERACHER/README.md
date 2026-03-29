# 🏨 AI Hotel Booking Chatbot

> An intelligent hotel recommendation system powered by Natural Language Processing and Machine Learning

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.14-green)
![Flask](https://img.shields.io/badge/flask-3.1.2-orange)
![License](https://img.shields.io/badge/license-MIT-purple)

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [AI Modules](#ai-modules)
- [Team](#team)

## ✨ Features

### 🤖 AI-Powered Features

- **Natural Language Query Processing** - Understand complex user queries like "Find me a cheap hotel near Al-Haram with WiFi"
- **Sentiment Analysis** - Analyze hotel reviews and extract guest sentiment
- **Fuzzy Location Matching** - Match user queries with landmarks using fuzzy string matching
- **Smart Recommendations** - Intelligent hotel ranking based on multiple criteria:
  - Distance (30%)
  - Price (25%)
  - Rating (25%)
  - Amenity Match (20%)

### 🌐 User Features

- **Interactive Chatbot Interface** - Natural conversation flow
- **Interactive Map** - Visualize hotel locations with Leaflet.js
- **Real-time Search** - Instant hotel recommendations
- **Hotel Details Modal** - Detailed view with reviews and sentiment analysis
- **Quick Action Buttons** - Fast access to common searches
- **Responsive Design** - Works on desktop and mobile

### 📊 Database

- **34 Hotels** across 4 Saudi Arabian cities (Makkah, Madinah, Riyadh, Jeddah)
- **46 Guest Reviews** with sentiment scores
- **16 Major Landmarks** with GPS coordinates

## 📁 Project Structure

```
CS331_Project/
├── backend/
│   ├── ai_modules/
│   │   ├── query_parser.py          # Natural language query parser
│   │   ├── sentiment_analyzer.py    # Review sentiment analysis
│   │   ├── location_matcher.py      # Fuzzy landmark matching
│   │   └── recommendation.py        # Hotel recommendation engine
│   ├── api/
│   │   └── routes.py                # Flask API endpoints
│   ├── database/
│   │   ├── schema.sql               # MySQL database schema
│   │   ├── db_connection.py         # Database connection & helpers
│   │   └── models.py                # Data models
│   ├── utils/
│   │   └── distance_calculator.py   # Geospatial distance calculations
│   ├── app.py                       # Main Flask application
│   ├── config.py                    # Configuration settings
│   └── requirements.txt             # Python dependencies
├── frontend/
│   ├── css/
│   │   └── style.css                # Application styles
│   ├── js/
│   │   ├── app.js                   # Main application logic
│   │   ├── chatbot.js               # Chatbot functionality
│   │   └── map.js                   # Map integration
│   └── index.html                   # Main HTML file
├── database/
│   └── schema.sql                   # Database schema (copy)
└── PROJECT_GUIDE.md                 # Development guide
```

## 🚀 Installation

### Prerequisites

- Python 3.14+
- MySQL 8.0+
- Modern web browser

### 1. Clone the Repository

```bash
cd C:\Users\abomo\OneDrive\Desktop\College\471-Semester\CS331\CS331Project\CS331_Project
```

### 2. Set Up MySQL Database

```bash
# Start MySQL server
# Run the schema
mysql -u root -p < database/schema.sql
```

**Database Credentials (update in `backend/config.py`):**

- Host: localhost
- User: root
- Password: Modtha@7
- Database: hotel_booking_ai

### 3. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Required Packages:**

- Flask 3.1.2 - Web framework
- Flask-CORS 6.0.1 - Cross-origin resource sharing
- mysql-connector-python 9.5.0 - MySQL database connector
- TextBlob 0.19.0 - Natural language processing
- FuzzyWuzzy 0.18.0 - Fuzzy string matching
- Pandas 2.3.3 - Data manipulation
- Geopy 2.4.1 - Geographic calculations

### 4. Download NLTK Data (for TextBlob)

```bash
python -m textblob.download_corpora
```

## 🎯 Running the Application

### Start the Backend API Server

```bash
cd backend
python app.py
```

Server will start on `http://127.0.0.1:5000`

### Start the Frontend Server

```bash
cd frontend
python -m http.server 8000
```

Open `http://localhost:8000` in your browser

## 📚 API Documentation

### Base URL

```
http://127.0.0.1:5000/api
```

### Endpoints

#### 1. Health Check

```http
GET /api/health
```

**Response:**

```json
{
  "status": "healthy",
  "message": "Hotel Booking AI API is running"
}
```

#### 2. Chat (Main Chatbot Endpoint)

```http
POST /api/chat
Content-Type: application/json

{
  "message": "Find me a cheap hotel near Al-Haram with WiFi",
  "user_location": {
    "lat": 21.4225,
    "lng": 39.8262
  }
}
```

**Response:**

```json
{
  "intent": "search",
  "message": "I found 5 hotels near Al-Haram Al-Makki matching your preferences:",
  "filters_used": {
    "location": "haram",
    "city": "Makkah",
    "price_preference": "low",
    "amenities": ["WiFi"]
  },
  "landmark": {
    "name": "Al-Haram Al-Makki",
    "coordinates": [21.4225, 39.8262]
  },
  "hotels": [
    {
      "id": 1,
      "name": "Hotel Name",
      "city": "Makkah",
      "star_rating": 4.5,
      "price_per_night": 350,
      "amenities": ["WiFi", "Parking"],
      "coordinates": { "lat": 21.4244, "lng": 39.8267 },
      "recommendation_score": 91.2,
      "distance": "220 meters",
      "explanation": "Recommended (Match: 91.2%) - Excellent location, great value..."
    }
  ],
  "total_found": 8
}
```

#### 3. Get All Hotels

```http
GET /api/hotels
GET /api/hotels?city=Makkah
```

#### 4. Get Hotel Details

```http
GET /api/hotels/{hotel_id}
```

Returns hotel info, reviews, and sentiment analysis.

#### 5. Get Nearby Hotels

```http
POST /api/hotels/nearby
Content-Type: application/json

{
  "latitude": 21.4225,
  "longitude": 39.8262,
  "radius_km": 5,
  "count": 10
}
```

#### 6. Get Landmarks

```http
GET /api/landmarks
```

## 🧠 AI Modules

### 1. Query Parser (`query_parser.py`)

**Purpose:** Parse natural language queries and extract search criteria

**Features:**

- Extract location/city/landmark
- Identify price preferences (cheap, affordable, luxury)
- Detect amenity requirements (WiFi, Pool, Gym, etc.)
- Extract rating requirements
- Classify intent (greeting, search, help, info)

**Example:**

```python
query = "Find me a cheap hotel near Al-Haram with WiFi"
result = {
    'location': 'haram',
    'city': 'Makkah',
    'price_preference': 'low',
    'amenities': ['WiFi'],
    'intent': 'search'
}
```

### 2. Sentiment Analyzer (`sentiment_analyzer.py`)

**Purpose:** Analyze hotel review sentiment using TextBlob

**Features:**

- Calculate polarity (-1 to 1) and subjectivity (0 to 1)
- Classify reviews as positive/negative/neutral
- Extract mentioned aspects (location, cleanliness, staff, etc.)
- Generate natural language summaries
- Compare sentiment across multiple hotels

**Example:**

```python
reviews = [
    {"review_text": "Great hotel with excellent service!", "rating": 5},
    {"review_text": "Terrible experience, very dirty.", "rating": 1}
]
result = {
    'average_polarity': 0.15,
    'distribution': {'positive': 60%, 'neutral': 20%, 'negative': 20%},
    'summary': "Based on 5 reviews, 60% of guests had a positive experience..."
}
```

### 3. Location Matcher (`location_matcher.py`)

**Purpose:** Match user location queries with database landmarks using fuzzy matching

**Features:**

- Fuzzy string matching with 70% threshold
- Text normalization (remove prefixes, hyphens)
- GPS coordinate retrieval
- Suggest multiple matches for ambiguous queries

**Example:**

```python
match_landmark("alharam")
# Returns: Al-Haram Al-Makki (100% confidence, 21.4225, 39.8262)

match_landmark("mosque")
# Returns: [Al-Haram Al-Makki, Prophet's Mosque, Quba Mosque]
```

### 4. Distance Calculator (`distance_calculator.py`)

**Purpose:** Calculate geodesic distances using Geopy

**Features:**

- Calculate distance between two GPS coordinates
- Add distances to hotel lists
- Sort hotels by proximity
- Filter by radius
- Human-readable distance descriptions

**Example:**

```python
distance = calculate_distance((21.4225, 39.8262), (24.4672, 39.6108))
# Returns: 337.9 km

format_distance(0.5)
# Returns: "500 meters"
```

### 5. Recommendation Engine (`recommendation.py`)

**Purpose:** Score and rank hotels based on multiple criteria

**Scoring Algorithm:**

```
Total Score =
  Distance Score × 30% +
  Price Score × 25% +
  Rating Score × 25% +
  Amenity Score × 20%
```

**Features:**

- Configurable scoring weights
- Price preference matching
- Amenity requirement matching
- Rating threshold filtering
- Natural language explanations

**Example:**

```python
user_preferences = {
    'price_preference': 'low',
    'min_rating': 3.5,
    'requested_amenities': ['WiFi', 'Parking']
}
recommendations = get_top_recommendations(hotels, user_preferences, count=5)
# Returns: Top 5 hotels sorted by recommendation score (0-100)
```

## 🧪 Testing

### Test Individual Modules

```bash
# Test Query Parser
python ai_modules/query_parser.py

# Test Sentiment Analyzer
python ai_modules/sentiment_analyzer.py

# Test Location Matcher
python ai_modules/location_matcher.py

# Test Distance Calculator
python utils/distance_calculator.py

# Test Recommendation Engine
python ai_modules/recommendation.py
```

### Test API

```bash
# While backend is running
python test_api.py
```

## 👥 Team

- **Rida Alajmi**
- **Mohammed Moawwadh**
- **Abdulelah ALLUQMANI**
- **Khalid Alshiha**

**Course:** CS331 - Artificial Intelligence  
**Institution:** King Saud University

## 📝 License

MIT License - feel free to use this project for learning purposes.

## 🎓 Academic Notes

### AI Concepts Demonstrated:

1. **Natural Language Processing (NLP)** - Query parsing with keyword extraction
2. **Sentiment Analysis** - TextBlob polarity and subjectivity analysis
3. **Fuzzy Matching** - FuzzyWuzzy for approximate string matching
4. **Machine Learning** - Multi-criteria recommendation system
5. **Geospatial Computing** - Distance calculations and location-based search

### Technologies Used:

- **Backend:** Python, Flask, MySQL
- **Frontend:** HTML5, CSS3, JavaScript, Leaflet.js
- **AI/ML:** TextBlob, FuzzyWuzzy, Pandas
- **Database:** MySQL with JSON fields

## 🚀 Future Enhancements

- [ ] Google Maps API integration for real hotel data
- [ ] User authentication and booking history
- [ ] Deep learning models (BERT, GPT) for better NLP
- [ ] Multi-language support (Arabic + English)
- [ ] Hotel price prediction using regression
- [ ] Collaborative filtering recommendations
- [ ] Real-time availability checking

## 📞 Support

For questions or issues, please contact the team members or refer to `PROJECT_GUIDE.md` for detailed implementation guidance.

---

**Made with ❤️ for CS331 AI Course Project**

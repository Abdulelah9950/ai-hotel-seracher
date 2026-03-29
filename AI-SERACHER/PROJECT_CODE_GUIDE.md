# CS331 AI Hotel Booking Chatbot - Code Structure & Key Components

## 📂 Project Directory Structure

```
CS331_Project/
├── backend/
│   ├── app.py                          # Flask application entry point
│   ├── config.py                       # Configuration & AI settings
│   ├── requirements.txt                # Python dependencies
│   │
│   ├── api/
│   │   ├── routes.py                   # Main API endpoints (MOST IMPORTANT)
│   │   └── __init__.py
│   │
│   ├── ai_modules/                     # AI/NLP Core Components
│   │   ├── query_parser.py            # Parse user queries → extract intent, filters
│   │   ├── sentiment_analyzer.py      # Analyze sentiment from reviews
│   │   ├── location_matcher.py        # Match location references
│   │   ├── recommendation.py          # Score & rank hotels
│   │   └── __init__.py
│   │
│   ├── database/
│   │   ├── db_connection.py           # MySQL connection management
│   │   ├── models.py                  # Database schema definitions
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── geoapify_service.py        # Geoapify Places API wrapper
│   │   ├── google_places.py           # Google Places API integration
│   │   └── __init__.py
│   │
│   └── utils/
│       ├── distance_calculator.py     # Calculate distances between points
│       ├── fetch_hotels_from_google.py
│       ├── google_maps.py
│       └── __init__.py
│
├── frontend/
│   ├── chatbot.html                   # Main UI (MOST IMPORTANT)
│   ├── css/
│   │   └── style.css                  # Styling
│   └── js/
│       ├── app.js                     # Main application logic
│       ├── chatbot.js                 # Chat handling & display
│       └── map.js                     # Leaflet map integration
│
├── database/
│   └── schema.sql                     # MySQL database schema
│
└── data/
    └── sample_hotels.csv              # Sample hotel data
```

---

## 🤖 AI/NLP Packages Used

### 1. **TextBlob** (v0.17.1) - NLP Sentiment Analysis
   - **Purpose**: Extract sentiment from hotel reviews
   - **File**: `backend/ai_modules/sentiment_analyzer.py`
   - **Key Method**: `analyze_review_sentiment(review_text)`
   - **Use Case**: Calculate review sentiment scores (-1.0 to 1.0)

### 2. **FuzzyWuzzy** (v0.18.0) - Fuzzy String Matching
   - **Purpose**: Match landmark names despite typos/variations
   - **File**: `backend/api/routes.py` (lines 186-210)
   - **Key Method**: `fuzz.ratio()` - Fuzzy match landmark names
   - **Use Case**: "Prophets Mosque" matches "Prophet's Mosque" even with different spelling

### 3. **GeoPy** (v2.4.1) - Geographic Distance Calculation
   - **Purpose**: Calculate distances between coordinates
   - **File**: `backend/utils/distance_calculator.py`
   - **Key Method**: `distance.distance((lat1, lon1), (lat2, lon2)).km`
   - **Use Case**: Find hotels within X km of a landmark

### 4. **Pandas** (v2.2.0+) - Data Processing
   - **Purpose**: Process hotel data and calculate statistics
   - **File**: Multiple modules (data filtering, sorting)
   - **Key Method**: DataFrame operations for filtering hotels

### 5. **Requests** (v2.31.0) - HTTP API Calls
   - **Purpose**: Call external APIs (Geoapify, Google Places)
   - **File**: `backend/services/geoapify_service.py`, `google_places.py`
   - **Key Method**: `requests.get()`, `requests.post()`

### 6. **GoogleMaps** (v4.10.0) - Google Maps Integration
   - **Purpose**: Geocoding, place searches
   - **File**: `backend/utils/google_maps.py`, `services/google_places.py`
   - **Key Method**: Client API calls for place information

---

## 📌 Most Important Files & Methods

### **1. backend/api/routes.py** - Core API Handler (MOST CRITICAL)
**Purpose**: Main endpoint processing all chatbot requests

**Key Methods**:

#### `@api_bp.route('/chat', methods=['POST'])` (Lines ~70-370)
```python
def chat():
    """
    Main chatbot endpoint - Process user query and return hotel recommendations
    
    Flow:
    1. Parse user message using QueryParser
    2. Extract intent (greeting/help/search)
    3. Extract filters (city, landmark, price, amenities)
    4. Search hotels from Geoapify API
    5. Calculate distances to landmark
    6. Score hotels using recommendation engine
    7. Return ranked results with amenities
    """
```

**Key Sub-Logic in chat()** (Lines 186-210):
```python
# Fuzzy match landmark names
from fuzzywuzzy import fuzz

for landmark_key in LANDMARKS:
    if fuzz.ratio(landmark_query, landmark_key) > 85:  # 85% match threshold
        matched_landmark = LANDMARKS[landmark_key]
        reference_point = (matched_landmark['latitude'], matched_landmark['longitude'])
```

**Amenities Extraction** (Lines 305-370):
```python
def extract_amenities_from_categories(categories):
    """
    Convert Geoapify categories to human-readable amenities
    Maps: 'internet_access' → 'WiFi', 'restaurant' → 'Restaurant', etc.
    """
    amenity_mapping = {
        'internet_access': 'WiFi',
        'wheelchair.yes': 'Wheelchair Accessible',
        # ... more mappings
    }
```

**LANDMARKS Dictionary** (Lines 25-37):
```python
LANDMARKS = {
    'al-haram': {'name': 'Al-Haram (Kaaba)', 'city': 'Makkah', 'latitude': 21.4225, 'longitude': 39.8262},
    'prophet\'s mosque': {'name': 'Prophet\'s Mosque', 'city': 'Madinah', 'latitude': 24.4703, 'longitude': 39.6068},
    # ... more landmarks
}
```

---

### **2. backend/ai_modules/query_parser.py** - NLP Query Processing
**Purpose**: Parse natural language → extract search parameters

**Key Methods**:

#### `parse(user_query)` (Lines ~300+)
```python
def parse(user_query):
    """
    Parse user input and extract:
    - Intent: greeting/help/search
    - City/Location
    - Landmark reference
    - Price preference (cheap/medium/luxury)
    - Required amenities (WiFi, Pool, etc.)
    - Star rating requirement
    
    Returns: dict with extracted parameters
    """
```

#### `_extract_landmark(query)` (Lines ~285)
```python
def _extract_landmark(self, query):
    """
    Detect landmark mentions in query
    Keywords: 'haram', 'prophet mosque', 'masjid', 'kingdom centre', etc.
    """
    landmarks = ['haram', 'al-haram', 'prophet\'s mosque', 'prophets mosque', 
                 'masjid nabawi', 'masjid al-nabawi', 'al-masjid an-nabawi', ...]
    
    for landmark in landmarks:
        if landmark in query:
            return landmark
```

#### `_extract_price_preference(query)` (Lines ~230)
```python
def _extract_price_preference(self, query):
    """
    Extract price preference: 'cheap' / 'luxury' / 'affordable'
    """
    for preference, keywords in self.price_keywords.items():
        for keyword in keywords:
            if keyword in query:
                return preference
```

#### `_extract_amenities(query)` (Lines ~250)
```python
def _extract_amenities(self, query):
    """
    Extract desired amenities: WiFi, Pool, Parking, Gym, Spa, Restaurant
    """
    found_amenities = []
    for amenity, keywords in self.amenity_keywords.items():
        for keyword in keywords:
            if keyword in query:
                found_amenities.append(amenity)
    return found_amenities
```

---

### **3. backend/ai_modules/sentiment_analyzer.py** - Review Analysis
**Purpose**: Analyze hotel review sentiment

**Key Methods**:

#### `analyze_review_sentiment(review_text)` (Lines ~40+)
```python
def analyze_review_sentiment(self, review_text):
    """
    Uses TextBlob to analyze sentiment
    Returns: float from -1.0 (negative) to +1.0 (positive)
    
    Process:
    1. Create TextBlob from review text
    2. Extract polarity (-1 to +1)
    3. Convert to rating influence
    """
    blob = TextBlob(review_text)
    polarity = blob.sentiment.polarity  # -1 to +1
    return polarity
```

---

### **4. backend/ai_modules/recommendation.py** - Hotel Ranking
**Purpose**: Score and rank hotels based on multiple factors

**Key Methods**:

#### `score_hotels(hotels, filters, reference_point)` (Lines ~50+)
```python
def score_hotels(self, hotels, filters, reference_point=None):
    """
    Calculate recommendation score for each hotel
    
    Scoring factors:
    - Distance to landmark (closer = higher score)
    - Amenities match (more matches = higher score)
    - Review ratings (higher rating = higher score)
    - Price match (matches preference = higher score)
    - Sentiment from reviews (positive = higher score)
    
    Final Score = weighted sum of all factors
    Returns: sorted hotels by score (highest first)
    """
```

---

### **5. backend/services/geoapify_service.py** - API Integration
**Purpose**: Fetch real-time hotel data from Geoapify Places API

**Key Methods**:

#### `search_places(query, location, radius)` (Lines ~30+)
```python
def search_places(self, query, location, radius=5000):
    """
    Call Geoapify API to search for hotels
    
    API Endpoint: https://api.geoapify.com/v2/places
    
    Params:
    - query: search term (e.g., "hotel")
    - location: (lat, lng) - center point
    - radius: search radius in meters (default 5km)
    
    Returns: List of hotels with:
    - name, location, rating
    - categories (for amenities extraction)
    - address, phone, website
    """
```

---

### **6. backend/utils/distance_calculator.py** - Distance Computation
**Purpose**: Calculate distances using GeoPy

**Key Methods**:

#### `calculate_distance(lat1, lon1, lat2, lon2)` (Lines ~20+)
```python
def calculate_distance(self, lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates (haversine formula)
    
    Uses: geopy.distance.distance()
    
    Returns: distance in kilometers
    """
    from geopy.distance import distance
    return distance((lat1, lon1), (lat2, lon2)).km
```

---

### **7. frontend/js/app.js** - Frontend State Management
**Purpose**: Manage application state and UI updates

**Key Methods**:

#### `toggleMap()` (Lines 114-159)
```javascript
function toggleMap() {
    /**
     * Toggle map visibility and load user location
     * 
     * Process:
     1. Get user geolocation (browser API)
     2. Initialize Leaflet map
     3. Add user location marker
     4. Add landmark marker
     5. Add hotel markers with scoring colors
     */
}
```

#### `getUserLocation()` (Lines 154+)
```javascript
function getUserLocation() {
    /**
     * Request browser geolocation permission
     * Store in AppState.userLocation
     * Used for: distance calculations, map centering
     */
    navigator.geolocation.getCurrentPosition(success, error, options)
}
```

---

### **8. frontend/js/chatbot.js** - Chat Interface
**Purpose**: Handle chat messages and hotel display

**Key Methods**:

#### `sendMessage()` (Lines ~40+)
```javascript
function sendMessage() {
    /**
     * Process user message:
     1. Send message to backend /api/chat
     2. Display user message
     3. Show typing indicator
     4. Parse response
     5. Display hotels with details modal
     6. Add click handlers for hotel details
     */
}
```

#### `displayHotel(hotel)` (Lines ~150+)
```javascript
function displayHotel(hotel) {
    /**
     * Create HTML for hotel card
     
     Displays:
     - Hotel name & rating
     - Distance to landmark
     - Price & star rating
     - ✨ Amenities section (WiFi, Restaurant, Pool, etc.)
     - Click to view details
     */
}
```

---

### **9. frontend/js/map.js** - Map Integration
**Purpose**: Leaflet.js map display and markers

**Key Methods**:

#### `initializeMap()` (Lines ~30+)
```javascript
function initializeMap() {
    /**
     * Initialize Leaflet map on port 5000
     * Center on Makkah/user location
     * Create L.tileLayer (OpenStreetMap)
     */
}
```

#### `updateMapMarkers(hotels, landmark)` (Lines ~80+)
```javascript
function updateMapMarkers(hotels, landmark) {
    /**
     * Add markers to map:
     1. Landmark marker (red mosque icon 🕌)
     2. User location marker (blue pin 📍)
     3. Hotel markers (color-coded by score)
        - Green: High score (8-10)
        - Yellow: Medium score (5-7)
        - Red: Low score (0-4)
     */
}
```

#### `addUserLocationMarker(lat, lng)` (Lines 148+)
```javascript
function addUserLocationMarker(lat, lng) {
    /**
     * Add blue marker showing user current location
     * Called when map is toggled visible
     */
}
```

---

## 🔄 Data Flow Diagram

```
User Input (Chatbot)
       ↓
   [app.js] getUserLocation()
       ↓
   [chatbot.js] sendMessage()
       ↓
   POST /api/chat (backend/api/routes.py)
       ↓
   [query_parser.py] parse() → Extract intent, city, landmark, amenities
       ↓
   Fuzzy Match LANDMARKS dictionary
       ↓
   [geoapify_service.py] search_places() → Fetch hotels from API
       ↓
   [distance_calculator.py] calculate_distance() → Distance to landmark
       ↓
   [sentiment_analyzer.py] analyze_review_sentiment() → Review scores
       ↓
   [recommendation.py] score_hotels() → Rank by score
       ↓
   Extract amenities from categories
       ↓
   Return ranked hotels with amenities
       ↓
   [chatbot.js] displayHotel() → Show results
       ↓
   [map.js] updateMapMarkers() → Plot on map with user location
```

---

## 📊 Configuration

**File**: `backend/config.py`

```python
AI_CONFIG = {
    'PRICE_RANGES': {
        'low': (0, 300),
        'medium': (300, 800),
        'high': (800, 5000)
    },
    'AMENITIES': ['WiFi', 'Restaurant', 'Parking', 'Pool', 'Gym', 'Spa', 'Bar'],
    'FUZZY_MATCH_THRESHOLD': 85,  # % similarity for landmark matching
}
```

---

## 🗄️ Database

**File**: `database/schema.sql`

**Tables**:
- `hotels` - Hotel information
- `reviews` - User reviews with sentiment
- `landmarks` - Location reference points
- `bookings` - User bookings

---

## Summary

| Component | Purpose | Key Technology |
|-----------|---------|-----------------|
| **query_parser.py** | Parse user intent | TextBlob, Regex |
| **sentiment_analyzer.py** | Analyze reviews | TextBlob sentiment |
| **location_matcher.py** | Match locations | FuzzyWuzzy |
| **recommendation.py** | Score hotels | Weighted scoring algorithm |
| **geoapify_service.py** | Fetch hotels | Geoapify API, Requests |
| **distance_calculator.py** | Calculate distances | GeoPy |
| **routes.py** | Main API logic | Flask, Fuzzy matching |
| **app.js** | Frontend state | JavaScript, Geolocation API |
| **map.js** | Display map | Leaflet.js, OpenStreetMap |
| **chatbot.js** | Chat interface | JavaScript, DOM manipulation |


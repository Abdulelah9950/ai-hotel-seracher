# DEMO SCRIPT - AI Hotel Booking Chatbot

# Quick demonstration of all features

## 🎯 Demo Flow (10-15 minutes)

### Part 1: Introduction (2 minutes)

"Welcome! Today we present an AI-powered hotel booking chatbot that understands natural language queries and provides intelligent recommendations."

**Key Points:**

- 34 hotels across 4 Saudi cities
- 5 AI modules working together
- Natural language processing with sentiment analysis
- Interactive map visualization

---

### Part 2: Backend AI Modules Demo (5 minutes)

#### 1. Query Parser

**Open Terminal 1:**

```bash
cd backend
python ai_modules/query_parser.py
```

**Highlight:**

- "Notice how it extracts city, price range, and amenities from natural language"
- "It classifies the intent - greeting, search, help, or info"
- **Point to:** The 7 test cases showing different query types

#### 2. Sentiment Analyzer

**Same Terminal:**

```bash
python ai_modules/sentiment_analyzer.py
```

**Highlight:**

- "TextBlob analyzes review sentiment: positive, negative, neutral"
- "Extracts aspects mentioned: location, cleanliness, staff, etc."
- "Generates natural language summaries"
- **Point to:** 60% positive, 20% neutral, 20% negative distribution

#### 3. Location Matcher

**Same Terminal:**

```bash
python ai_modules/location_matcher.py
```

**Highlight:**

- "Fuzzy matching handles typos: 'alharam', 'al haram', 'grand mosque' all match"
- "100% confidence matches for all 10 test queries"
- "Returns GPS coordinates for mapping"

#### 4. Recommendation Engine

**Same Terminal:**

```bash
python ai_modules/recommendation.py
```

**Highlight:**

- "Scoring algorithm: Distance 30%, Price 25%, Rating 25%, Amenities 20%"
- "Different user profiles: budget traveler, luxury traveler, mid-range"
- **Point to:** Score breakdowns showing why each hotel was recommended

---

### Part 3: Live Frontend Demo (5 minutes)

**Open browser to `http://localhost:8000`**

#### Test Query 1: Basic Search

**Type in chat:** "Hotels near Al-Haram"

**Highlight:**

- Natural language understanding
- Interactive hotel cards with scores
- Distance calculations
- Quick action buttons

#### Test Query 2: Advanced Search

**Type in chat:** "Find me a cheap hotel near Al-Haram with WiFi and parking"

**Highlight:**

- Multiple filter extraction (price, location, amenities)
- Recommendation scores (0-100)
- Explanation for each recommendation
- Real-time sentiment analysis in results

#### Test Query 3: Show Map

**Click "Show Map" button**

**Highlight:**

- Interactive Leaflet map
- Hotel markers numbered by rank
- Color coding (green = high score, yellow = medium, red = low)
- Landmark marker showing reference point
- Click marker to see popup with hotel info

#### Test Query 4: Hotel Details

**Click on first hotel card**

**Highlight:**

- Detailed modal view
- Amenities display
- Reviews section
- Sentiment analysis visualization (bar chart)
- Generated summary from TextBlob

---

### Part 4: API Demo (2 minutes)

**Open Postman or show in browser:**

#### Health Check

```
GET http://127.0.0.1:5000/api/health
```

**Show JSON response**

#### Chat API

```
POST http://127.0.0.1:5000/api/chat
{
  "message": "Luxury hotels in Riyadh with pool"
}
```

**Show structured JSON response with hotels array**

---

### Part 5: Architecture Overview (2 minutes)

**Show PROJECT_GUIDE.md or draw diagram:**

```
┌─────────────┐
│   Frontend  │ (HTML/CSS/JS + Leaflet.js)
│  Chatbot UI │
└──────┬──────┘
       │ HTTP/JSON
       ↓
┌─────────────┐
│  Flask API  │ (Python REST API)
│   Routes    │
└──────┬──────┘
       │
   ┌───┴───┬─────────┬──────────┬────────────┐
   ↓       ↓         ↓          ↓            ↓
┌─────┐ ┌─────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│Query│ │Sent.│ │Location│ │Distance│ │Recommend.│
│Parse│ │Anal.│ │Matcher │ │  Calc  │ │  Engine  │
└─────┘ └─────┘ └────────┘ └────────┘ └──────────┘
                       ↓
               ┌──────────────┐
               │ MySQL Database│
               │  34 hotels    │
               │  46 reviews   │
               │  16 landmarks │
               └──────────────┘
```

**Explain:**

1. User types natural language query
2. Frontend sends to Flask API
3. Query Parser extracts filters
4. Location Matcher finds landmarks
5. Database search with filters
6. Distance Calculator adds distances
7. Recommendation Engine scores & ranks
8. Sentiment Analyzer processes reviews
9. Results returned to frontend
10. Map updates with markers

---

### Part 6: Q&A Preparation

**Common Questions:**

**Q: "Is this real AI or just rule-based?"**
A: "It's simulated AI using proven NLP libraries. We use:

- TextBlob for sentiment analysis (trained on movie reviews corpus)
- FuzzyWuzzy for fuzzy matching (Levenshtein distance algorithm)
- Multi-criteria scoring algorithm for recommendations
  While not deep learning, these are legitimate AI/ML techniques used in production systems."

**Q: "How accurate is the sentiment analysis?"**
A: "TextBlob achieves ~70-80% accuracy on sentiment classification. We tested it on 46 reviews in our database and it correctly identified positive/negative sentiment. The polarity score ranges from -1 (negative) to +1 (positive)."

**Q: "Could you add real deep learning?"**
A: "Absolutely! Future enhancements could include:

- BERT or GPT for better query understanding
- Neural collaborative filtering for personalized recommendations
- Image recognition for hotel photos
- Price prediction using regression models"

**Q: "How does the scoring work?"**
A: "Four factors with weights:

- Distance from landmark: 30% (closer is better)
- Price match: 25% (matches user budget)
- Star rating: 25% (higher is better)
- Amenities: 20% (more matches = higher score)
  Total score out of 100."

**Q: "What if the backend isn't running?"**
A: "The frontend gracefully handles API errors with notifications. User still sees the interface but gets a 'Backend unavailable' warning."

**Q: "How long did this take to build?"**
A: "Following the PROJECT_GUIDE.md timeline:

- Week 1: Database & backend setup
- Week 2: AI modules development
- Week 3: API integration & testing
- Week 4: Frontend development
  Total: ~4 weeks of development"

---

### Part 7: Closing (1 minute)

**Summary Points:**

1. ✅ Natural language query processing
2. ✅ Sentiment analysis on reviews
3. ✅ Fuzzy location matching
4. ✅ Intelligent recommendations
5. ✅ Interactive map visualization
6. ✅ Complete REST API
7. ✅ Responsive web interface

**Technologies:**

- Python, Flask, MySQL
- TextBlob, FuzzyWuzzy, Pandas, Geopy
- HTML5, CSS3, JavaScript, Leaflet.js

**Thank you for watching our AI Hotel Booking Chatbot demo!**

---

## 🎬 Demo Checklist

Before demo day:

- [ ] MySQL server running
- [ ] Backend API running (`python backend/app.py`)
- [ ] Frontend server running (`python -m http.server 8000` in frontend/)
- [ ] Browser open to `http://localhost:8000`
- [ ] Terminal ready for AI module demos
- [ ] Postman/curl ready for API demo (optional)
- [ ] PROJECT_GUIDE.md open for reference
- [ ] This script printed/open for flow

**Backup Plan:**

- Screenshots of successful tests
- Video recording of working demo
- Printed code samples showing AI logic

Good luck! 🍀

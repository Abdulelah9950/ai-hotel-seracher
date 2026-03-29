# Query Parser Module
# Parse user queries and extract meaningful information

import re
from textblob import TextBlob
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AI_CONFIG


class QueryParser:
    """
    Parse natural language queries to extract search criteria
    """
    
    def __init__(self):
        """Initialize the query parser with keyword dictionaries"""
        
        # Price-related keywords
        self.price_keywords = {
            'low': ['cheap', 'affordable', 'budget', 'economical', 'inexpensive', 'low price', 'low cost'],
            'medium': ['moderate', 'reasonable', 'mid-range', 'average', 'fair price'],
            'high': ['luxury', 'premium', 'expensive', 'high-end', 'five-star', '5-star', 'upscale', 'deluxe']
        }
        
        # Amenity keywords mapping
        self.amenity_keywords = {
            'wifi': ['wifi', 'wi-fi', 'internet', 'wireless'],
            'pool': ['pool', 'swimming', 'swim'],
            'parking': ['parking', 'park', 'garage'],
            'gym': ['gym', 'fitness', 'exercise', 'workout'],
            'spa': ['spa', 'massage', 'wellness'],
            'restaurant': ['restaurant', 'dining', 'food', 'breakfast', 'dinner'],
            'room service': ['room service', 'room-service']
        }
        
        # Location keywords
        self.location_keywords = ['near', 'close to', 'around', 'by', 'next to', 'in', 'at']
        
        # Major cities worldwide (Saudi Arabia + International)
        self.cities = [
            # Saudi Arabia
            'makkah', 'madinah', 'riyadh', 'jeddah', 'mecca', 'medina',
            'yanbu', 'yanbue', 'yanbo', 'yenbu',
            'dammam', 'khobar', 'dhahran', 'taif', 'tabuk', 'abha', 'jizan', 'najran',
            'hail', 'buraidah', 'qatif', 'jubail',
            
            # UAE
            'dubai', 'abu dhabi', 'sharjah', 'ajman', 'ras al khaimah', 'fujairah', 'umm al quwain',
            
            # Middle East
            'cairo', 'alexandria', 'beirut', 'amman', 'kuwait', 'doha', 'manama', 'muscat',
            'baghdad', 'damascus', 'jerusalem', 'tel aviv', 'ankara', 'istanbul',
            
            # Europe
            'london', 'paris', 'berlin', 'rome', 'madrid', 'barcelona', 'amsterdam', 'brussels',
            'vienna', 'prague', 'budapest', 'warsaw', 'athens', 'lisbon', 'dublin', 'copenhagen',
            'stockholm', 'oslo', 'helsinki', 'zurich', 'geneva', 'munich', 'milan', 'venice',
            
            # North America
            'new york', 'los angeles', 'chicago', 'san francisco', 'miami', 'las vegas',
            'seattle', 'boston', 'washington', 'toronto', 'vancouver', 'montreal', 'mexico city',
            
            # Asia
            'tokyo', 'osaka', 'kyoto', 'beijing', 'shanghai', 'hong kong', 'singapore',
            'bangkok', 'kuala lumpur', 'jakarta', 'manila', 'seoul', 'taipei', 'hanoi',
            'mumbai', 'delhi', 'bangalore', 'karachi', 'lahore', 'dhaka',
            
            # Australia & Oceania
            'sydney', 'melbourne', 'brisbane', 'perth', 'auckland', 'wellington',
            
            # Africa
            'johannesburg', 'cape town', 'nairobi', 'casablanca', 'tunis', 'algiers',
            
            # South America
            'sao paulo', 'rio de janeiro', 'buenos aires', 'lima', 'bogota', 'santiago',
            
            # Countries (will be mapped to capital/major cities)
            'switzerland', 'france', 'germany', 'italy', 'spain', 'japan', 'china',
            'usa', 'united states', 'america', 'canada', 'australia', 'uae',
            'egypt', 'turkey', 'greece', 'portugal', 'netherlands', 'belgium',
            'austria', 'sweden', 'norway', 'denmark', 'finland', 'saudi arabia', 'saudi',
            'thailand', 'singapore', 'malaysia', 'india', 'brazil', 'mexico',
            'uk', 'united kingdom', 'england'
        ]
        
        # City name normalization (variant -> standard)
        self.city_normalization = {
            'mecca': 'Makkah',
            'medina': 'Madinah',
            'yanbue': 'Yanbu',
            'yanbo': 'Yanbu',
            'yenbu': 'Yanbu',
            'khobar': 'Al Khobar',
            'jizan': 'Jazan',
            'ny': 'New York',
            'la': 'Los Angeles',
            'sf': 'San Francisco',
            'dc': 'Washington',
            # Countries -> Capital/Major city
            'switzerland': 'Zurich',
            'france': 'Paris',
            'uk': 'London',
            'united kingdom': 'London',
            'england': 'London',
            'germany': 'Berlin',
            'italy': 'Rome',
            'spain': 'Madrid',
            'japan': 'Tokyo',
            'china': 'Beijing',
            'usa': 'New York',
            'united states': 'New York',
            'america': 'New York',
            'canada': 'Toronto',
            'australia': 'Sydney',
            'uae': 'Dubai',
            'egypt': 'Cairo',
            'turkey': 'Istanbul',
            'greece': 'Athens',
            'portugal': 'Lisbon',
            'netherlands': 'Amsterdam',
            'belgium': 'Brussels',
            'austria': 'Vienna',
            'sweden': 'Stockholm',
            'norway': 'Oslo',
            'denmark': 'Copenhagen',
            'finland': 'Helsinki',
            'saudi arabia': 'Riyadh',
            'saudi': 'Riyadh',
            'thailand': 'Bangkok',
            'singapore': 'Singapore',
            'malaysia': 'Kuala Lumpur',
            'india': 'Mumbai',
            'brazil': 'Sao Paulo',
            'mexico': 'Mexico City'
        }
        
        # Rating keywords
        self.rating_keywords = {
            5: ['five star', '5 star', '5-star', 'five-star', 'best rated', 'top rated'],
            4: ['four star', '4 star', '4-star', 'four-star', 'good rated', 'highly rated',
                'excellent', 'superior', 'quality'],
            3: ['three star', '3 star', '3-star', 'three-star', 'decent', 'good'],
            2: ['two star', '2 star', '2-star', 'two-star', 'basic']
        }
    
    def parse(self, query):
        """
        Parse user query and extract search criteria
        
        Args:
            query (str): User's natural language query
            
        Returns:
            dict: Parsed query with extracted filters
        """
        query_lower = query.lower().strip()
        
        result = {
            'original_query': query,
            'location': self._extract_location(query_lower),
            'city': self._extract_city(query_lower),
            'price_preference': self._extract_price_preference(query_lower),
            'price_range': self._extract_price_range(query_lower),
            'amenities': self._extract_amenities(query_lower),
            'min_rating': self._extract_rating(query_lower),
            'landmark': self._extract_landmark(query_lower),
            'intent': self._determine_intent(query_lower),
            'keywords': self._extract_keywords(query_lower)
        }
        
        return result
    
    def _extract_location(self, query):
        """Extract location mentions from query"""
        for keyword in self.location_keywords:
            if keyword in query:
                # Extract text after location keyword
                parts = query.split(keyword)
                if len(parts) > 1:
                    location_text = parts[1].strip().split()[0:3]  # Get next few words
                    return ' '.join(location_text)
        return None
    
    def _extract_city(self, query):
        """Extract city name from query"""
        for city in self.cities:
            if city in query:
                # Normalize city names using the mapping
                return self.city_normalization.get(city, city.capitalize())
        return None
    
    def _extract_price_preference(self, query):
        """
        Extract price preference (low, medium, high)
        
        Returns:
            str: 'low', 'medium', 'high', or None
        """
        for preference, keywords in self.price_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    return preference
        return None
    
    def _extract_price_range(self, query):
        """
        Extract specific price range from query
        
        Returns:
            tuple: (min_price, max_price) or None
        """
        # Look for patterns like "under 500", "below 400", "less than 300"
        under_match = re.search(r'(?:under|below|less than|max|maximum)\s+(\d+)', query)
        if under_match:
            max_price = int(under_match.group(1))
            return (0, max_price)
        
        # Look for patterns like "above 500", "over 400", "more than 300"
        over_match = re.search(r'(?:above|over|more than|min|minimum)\s+(\d+)', query)
        if over_match:
            min_price = int(over_match.group(1))
            return (min_price, 10000)
        
        # Look for patterns like "between 300 and 500", "300-500", "300 to 500"
        between_match = re.search(r'(?:between\s+)?(\d+)\s*(?:and|to|-)\s*(\d+)', query)
        if between_match:
            min_price = int(between_match.group(1))
            max_price = int(between_match.group(2))
            return (min_price, max_price)
        
        # Use price preference to set range
        preference = self._extract_price_preference(query)
        if preference:
            return AI_CONFIG['PRICE_RANGES'].get(preference)
        
        return None
    
    def _extract_amenities(self, query):
        """
        Extract required amenities from query
        
        Returns:
            list: List of amenity names (capitalized)
        """
        found_amenities = []
        
        for amenity, keywords in self.amenity_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    # Capitalize amenity name properly
                    if amenity == 'wifi':
                        found_amenities.append('WiFi')
                    elif amenity == 'room service':
                        found_amenities.append('Room Service')
                    else:
                        found_amenities.append(amenity.capitalize())
                    break
        
        return list(set(found_amenities))  # Remove duplicates
    
    def _extract_rating(self, query):
        """
        Extract minimum star rating from query
        
        Returns:
            float: Minimum rating or None
        """
        for rating, keywords in self.rating_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    return float(rating)
        
        # Look for numeric ratings
        rating_match = re.search(r'(\d+(?:\.\d+)?)\s*star', query)
        if rating_match:
            return float(rating_match.group(1))
        
        return None
    
    def _extract_landmark(self, query):
        """
        Extract landmark mentions from query
        
        Returns:
            str: Landmark name or None
        """
        # Common landmarks (will be matched with fuzzy matching later)
        landmarks = ['haram', 'al-haram', 'alharam', 'grand mosque', 'kaaba', 'masjid',
                    'prophet\'s mosque', 'prophets mosque', 'prophet mosque', 'masjid nabawi', 'masjid al-nabawi', 'al-masjid an-nabawi',
                    'mount arafat', 'arafat', 'quba', 'kingdom centre', 'kingdom tower',
                    'corniche', 'jinn mosque']
        
        for landmark in landmarks:
            if landmark in query:
                return landmark
        
        return None
    
    def _extract_keywords(self, query):
        """
        Extract important keywords using TextBlob
        
        Returns:
            list: List of important words
        """
        blob = TextBlob(query)
        
        # Get noun phrases and important words
        keywords = []
        
        # Add noun phrases
        for phrase in blob.noun_phrases:
            keywords.append(phrase)
        
        # Add important words (nouns, adjectives)
        for word, tag in blob.tags:
            if tag in ['NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS']:
                keywords.append(word.lower())
        
        # Remove common stop words
        stop_words = ['hotel', 'hotels', 'find', 'show', 'get', 'want', 'need', 'looking', 'search']
        keywords = [k for k in keywords if k not in stop_words]
        
        return list(set(keywords))[:10]  # Return top 10 unique keywords
    
    def _determine_intent(self, query):
        """
        Determine user's intent from query
        
        Returns:
            str: Intent type
        """
        # Greeting intent
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in query for greeting in greetings):
            return 'greeting'
        
        # Search intent
        search_words = ['find', 'search', 'look', 'show', 'get', 'want', 'need', 'recommend']
        if any(word in query for word in search_words):
            return 'search'
        
        # More info intent
        info_words = ['details', 'information', 'tell me more', 'about', 'reviews']
        if any(word in query for word in info_words):
            return 'info'
        
        # Help intent
        help_words = ['help', 'how to', 'can you', 'what can']
        if any(word in query for word in help_words):
            return 'help'
        
        # Default to search
        return 'search'
    
    def get_search_filters(self, parsed_query):
        """
        Convert parsed query to database search filters
        
        Args:
            parsed_query (dict): Result from parse() method
            
        Returns:
            dict: Filters ready for database query
        """
        filters = {}
        
        # Add city filter
        if parsed_query['city']:
            filters['city'] = parsed_query['city']
        
        # Add price range filter
        if parsed_query['price_range']:
            filters['min_price'] = parsed_query['price_range'][0]
            filters['max_price'] = parsed_query['price_range'][1]
        
        # Add amenities filter
        if parsed_query['amenities']:
            filters['amenities'] = parsed_query['amenities']
        
        # Add rating filter
        if parsed_query['min_rating']:
            filters['min_rating'] = parsed_query['min_rating']
        
        # Add limit
        filters['limit'] = AI_CONFIG['MAX_RESULTS']
        
        return filters


def test_query_parser():
    """Test the query parser with sample queries"""
    
    print("\n" + "=" * 60)
    print("Testing Query Parser")
    print("=" * 60)
    
    parser = QueryParser()
    
    # Test queries
    test_queries = [
        "Find me a cheap hotel in Makkah with WiFi",
        "Hotels near Al-Haram under 500 SAR",
        "Luxury hotel in Riyadh with pool and gym",
        "Show me 5-star hotels in Jeddah",
        "Budget hotel near Grand Mosque with parking",
        "Hotels in Madinah between 300 and 600 SAR",
        "I need an affordable hotel with breakfast"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}] Query: '{query}'")
        print("-" * 60)
        
        result = parser.parse(query)
        
        print(f"✓ Intent: {result['intent']}")
        if result['city']:
            print(f"✓ City: {result['city']}")
        if result['price_preference']:
            print(f"✓ Price Preference: {result['price_preference']}")
        if result['price_range']:
            print(f"✓ Price Range: {result['price_range'][0]}-{result['price_range'][1]} SAR")
        if result['amenities']:
            print(f"✓ Amenities: {', '.join(result['amenities'])}")
        if result['min_rating']:
            print(f"✓ Min Rating: {result['min_rating']} stars")
        if result['landmark']:
            print(f"✓ Landmark: {result['landmark']}")
        
        # Show search filters
        filters = parser.get_search_filters(result)
        print(f"✓ Search Filters: {filters}")
    
    print("\n" + "=" * 60)
    print("Query Parser is working perfectly!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_query_parser()

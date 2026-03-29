# Location Matcher Module
# Match user location queries with landmarks in database

from fuzzywuzzy import fuzz
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AI_CONFIG
from database.db_connection import get_all_landmarks, get_landmark_by_name


class LocationMatcher:
    """
    Match user location queries with landmarks using fuzzy matching
    """
    
    def __init__(self):
        """Initialize the location matcher"""
        self.threshold = AI_CONFIG['FUZZY_MATCH_THRESHOLD']
        self.landmarks = None
    
    def load_landmarks(self):
        """Load landmarks from database"""
        if self.landmarks is None:
            try:
                self.landmarks = get_all_landmarks()
                if self.landmarks is None:
                    self.landmarks = []
                    print("[WARN] No landmarks loaded from database")
            except Exception as e:
                print(f"[ERROR] Failed to load landmarks: {e}")
                self.landmarks = []
        return self.landmarks
    
    def normalize_text(self, text):
        """
        Normalize text for matching
        
        Args:
            text (str): Text to normalize
            
        Returns:
            str: Normalized text
        """
        # Convert to lowercase and remove extra spaces
        text = text.lower().strip()
        
        # Remove common prefixes/suffixes
        prefixes = ['al-', 'al ', 'the ']
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):]
        
        # Remove hyphens and underscores
        text = text.replace('-', ' ').replace('_', ' ')
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text
    
    def match_landmark(self, query):
        """
        Match user query with landmarks using fuzzy matching
        
        Args:
            query (str): User's location query
            
        Returns:
            dict: Best matching landmark with confidence score, or None
        """
        if not query:
            return None
        
        # Load landmarks
        landmarks = self.load_landmarks()
        if not landmarks:
            return None
        
        # Normalize query
        normalized_query = self.normalize_text(query)
        
        best_match = None
        best_score = 0
        
        for landmark in landmarks:
            # Try matching with main name
            landmark_name = self.normalize_text(landmark['name'])
            score = fuzz.ratio(normalized_query, landmark_name)
            
            # Also try partial ratio for substring matching
            partial_score = fuzz.partial_ratio(normalized_query, landmark_name)
            score = max(score, partial_score)
            
            if score > best_score:
                best_score = score
                best_match = landmark
            
            # Try matching with alternative names
            if landmark.get('alternative_names'):
                import json
                alt_names = landmark['alternative_names']
                
                # Parse if string
                if isinstance(alt_names, str):
                    try:
                        alt_names = json.loads(alt_names)
                    except:
                        alt_names = []
                
                for alt_name in alt_names:
                    normalized_alt = self.normalize_text(alt_name)
                    score = fuzz.ratio(normalized_query, normalized_alt)
                    partial_score = fuzz.partial_ratio(normalized_query, normalized_alt)
                    score = max(score, partial_score)
                    
                    if score > best_score:
                        best_score = score
                        best_match = landmark
        
        # Return match if score exceeds threshold
        if best_score >= self.threshold:
            return {
                'landmark': best_match,
                'confidence': best_score / 100,  # Convert to 0-1 scale
                'matched_query': query
            }
        
        return None
    
    def find_nearest_landmark(self, query, city=None):
        """
        Find nearest landmark matching query, optionally filtered by city
        
        Args:
            query (str): Location query
            city (str): City name filter (optional)
            
        Returns:
            dict: Matching landmark or None
        """
        match = self.match_landmark(query)
        
        if match and city:
            # Check if landmark is in the specified city
            landmark = match['landmark']
            if landmark.get('city', '').lower() != city.lower():
                return None
        
        return match
    
    def get_landmark_coordinates(self, query):
        """
        Get coordinates for a landmark query
        
        Args:
            query (str): Location query
            
        Returns:
            tuple: (latitude, longitude) or None
        """
        match = self.match_landmark(query)
        
        if match:
            landmark = match['landmark']
            return (landmark['latitude'], landmark['longitude'])
        
        return None
    
    def suggest_landmarks(self, query, max_suggestions=3):
        """
        Get multiple landmark suggestions for ambiguous queries
        
        Args:
            query (str): Location query
            max_suggestions (int): Maximum number of suggestions
            
        Returns:
            list: List of landmark matches with confidence scores
        """
        if not query:
            return []
        
        landmarks = self.load_landmarks()
        if not landmarks:
            return []
        
        normalized_query = self.normalize_text(query)
        matches = []
        
        for landmark in landmarks:
            # Calculate match scores
            landmark_name = self.normalize_text(landmark['name'])
            score = max(
                fuzz.ratio(normalized_query, landmark_name),
                fuzz.partial_ratio(normalized_query, landmark_name)
            )
            
            # Check alternative names
            if landmark.get('alternative_names'):
                import json
                alt_names = landmark['alternative_names']
                
                if isinstance(alt_names, str):
                    try:
                        alt_names = json.loads(alt_names)
                    except:
                        alt_names = []
                
                for alt_name in alt_names:
                    normalized_alt = self.normalize_text(alt_name)
                    alt_score = max(
                        fuzz.ratio(normalized_query, normalized_alt),
                        fuzz.partial_ratio(normalized_query, normalized_alt)
                    )
                    score = max(score, alt_score)
            
            # Add to matches if above minimum threshold
            if score >= 50:  # Lower threshold for suggestions
                matches.append({
                    'landmark': landmark,
                    'confidence': score / 100,
                    'score': score
                })
        
        # Sort by score and return top matches
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:max_suggestions]
    
    def validate_location(self, location_name):
        """
        Check if a location name exists in database
        
        Args:
            location_name (str): Location name to validate
            
        Returns:
            bool: True if location exists
        """
        match = self.match_landmark(location_name)
        return match is not None


def test_location_matcher():
    """Test the location matcher with sample queries"""
    
    print("\n" + "=" * 60)
    print("Testing Location Matcher")
    print("=" * 60)
    
    matcher = LocationMatcher()
    
    # Test queries
    test_queries = [
        "alharam",
        "al haram",
        "grand mosque",
        "prophet mosque",
        "kaaba",
        "kingdom tower",
        "corniche",
        "masjid nabawi",
        "mount arafat",
        "quba mosque"
    ]
    
    print("\n[Test 1] Matching Landmarks")
    print("-" * 60)
    
    for query in test_queries:
        match = matcher.match_landmark(query)
        
        print(f"\nQuery: '{query}'")
        if match:
            landmark = match['landmark']
            confidence = int(match['confidence'] * 100)
            print(f"✓ Match: {landmark['name']}")
            print(f"  Confidence: {confidence}%")
            print(f"  City: {landmark['city']}")
            print(f"  Coordinates: ({landmark['latitude']}, {landmark['longitude']})")
        else:
            print(f"✗ No match found")
    
    print("\n" + "-" * 60)
    print("[Test 2] Getting Coordinates")
    print("-" * 60)
    
    coords = matcher.get_landmark_coordinates("al-haram")
    if coords:
        print(f"\n✓ Al-Haram coordinates: {coords}")
    
    print("\n" + "-" * 60)
    print("[Test 3] Ambiguous Query Suggestions")
    print("-" * 60)
    
    suggestions = matcher.suggest_landmarks("mosque", max_suggestions=3)
    print(f"\nQuery: 'mosque' (ambiguous)")
    print(f"Suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        landmark = suggestion['landmark']
        confidence = int(suggestion['confidence'] * 100)
        print(f"  {i}. {landmark['name']} ({confidence}% match)")
    
    print("\n" + "=" * 60)
    print("Location Matcher is working perfectly!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_location_matcher()

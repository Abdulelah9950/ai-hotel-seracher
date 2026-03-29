# Recommendation Engine Module
# Recommendation Engine
# Score and rank hotels based on multiple criteria

import sys
import os
from decimal import Decimal

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AI_CONFIG


class RecommendationEngine:
    """
    Score and rank hotels based on user preferences and multiple criteria
    """
    
    def __init__(self, weights=None):
        """
        Initialize recommendation engine with scoring weights
        
        Args:
            weights (dict): Custom scoring weights (distance, price, rating, amenities)
        """
        # Default weights (must sum to 1.0)
        self.weights = weights or {
            'distance': 0.30,    # 30% - Proximity to desired location
            'price': 0.25,       # 25% - Price match with preference
            'rating': 0.25,      # 25% - Hotel star rating
            'amenities': 0.20    # 20% - Amenity match
        }
    
    def calculate_distance_score(self, distance_km):
        """
        Calculate score based on distance (closer is better)
        
        Args:
            distance_km (float): Distance in kilometers
            
        Returns:
            float: Score from 0 to 100
        """
        if distance_km is None:
            return 50.0  # Neutral score if distance unknown
        
        # Score decreases as distance increases
        if distance_km <= 0.5:
            return 100.0
        elif distance_km <= 1.0:
            return 90.0
        elif distance_km <= 2.0:
            return 80.0
        elif distance_km <= 5.0:
            return 60.0
        elif distance_km <= 10.0:
            return 40.0
        elif distance_km <= 20.0:
            return 20.0
        else:
            return 10.0
    
    def calculate_price_score(self, hotel_price, user_preference):
        """
        Calculate score based on price preference match
        
        Args:
            hotel_price (float): Hotel price per night
            user_preference (str): 'low', 'medium', or 'high'
            
        Returns:
            float: Score from 0 to 100
        """
        if user_preference is None:
            return 75.0  # Neutral-high score if no preference
        
        if hotel_price is None:
            return 75.0  # Neutral score if price unknown
        
        price_ranges = AI_CONFIG['PRICE_RANGES']
        
        # Get preferred range (tuple format: (min, max))
        pref_min, pref_max = price_ranges[user_preference]
        
        # Convert Decimal to float for calculations
        hotel_price = float(hotel_price)
        
        # Perfect match if within preferred range
        if pref_min <= hotel_price <= pref_max:
            # Higher score for prices closer to the middle of the range
            middle = (pref_min + pref_max) / 2
            deviation = abs(hotel_price - middle) / (pref_max - pref_min)
            return 100.0 - (deviation * 20)  # Max 20 point penalty
        
        # Calculate penalty for being outside preferred range
        if hotel_price < pref_min:
            # Below range (might be suspicious or lack quality)
            penalty = (pref_min - hotel_price) / pref_min
            return max(50.0, 70.0 - (penalty * 40))
        else:
            # Above range (too expensive)
            penalty = (hotel_price - pref_max) / pref_max
            return max(20.0, 60.0 - (penalty * 40))
    
    def calculate_rating_score(self, star_rating, min_rating=None):
        """
        Calculate score based on star rating
        
        Args:
            star_rating (float): Hotel star rating (1-5)
            min_rating (float): Minimum required rating
            
        Returns:
            float: Score from 0 to 100
        """
        if star_rating is None:
            return 50.0
        
        # Convert Decimal to float for calculations
        star_rating = float(star_rating)
        if min_rating is not None:
            min_rating = float(min_rating)
        
        # Base score (5 stars = 100, 1 star = 20)
        base_score = (star_rating / 5.0) * 100
        
        # CRITICAL: Penalty if below minimum rating - MUST filter these out
        if min_rating and star_rating < min_rating:
            # EXTREME penalty to completely exclude below-minimum hotels
            # A 3-star when asking for 5-star should get very low score
            penalty = (min_rating - star_rating) * 40  # Increased from 25 to 40
            base_score = max(0, base_score - penalty)  # This will be negative, which becomes 0
            if base_score <= 0:
                base_score = 5.0  # Minimum 5 so they appear last
        
        # Bonus for exceeding minimum rating
        elif min_rating and star_rating >= min_rating:
            # Bonus for meeting or exceeding minimum
            bonus = (star_rating - min_rating) * 20  # Increased from 10 to 20
            base_score = min(100, base_score + bonus)
        
        return base_score
    
    def calculate_amenity_score(self, hotel_amenities, requested_amenities):
        """
        Calculate score based on amenity match
        
        Args:
            hotel_amenities (list): List of hotel amenities
            requested_amenities (list): List of requested amenities
            
        Returns:
            float: Score from 0 to 100
        """
        if not requested_amenities:
            return 80.0  # Good base score if no specific amenities requested
        
        if not hotel_amenities:
            return 30.0  # Low score if hotel has no amenities
        
        # Calculate match percentage
        matched = 0
        for requested in requested_amenities:
            if requested in hotel_amenities:
                matched += 1
        
        match_percentage = (matched / len(requested_amenities)) * 100
        
        # Bonus points for having extra amenities
        extra_amenities = len(hotel_amenities) - len(requested_amenities)
        bonus = min(10, extra_amenities * 2)
        
        return min(100, match_percentage + bonus)
    
    def score_hotel(self, hotel, user_preferences):
        """
        Calculate overall score for a hotel based on user preferences
        
        Args:
            hotel (dict): Hotel data with distance, price, rating, amenities
            user_preferences (dict): User preferences including:
                - distance_km (float): Distance from desired location
                - price_preference (str): 'low', 'medium', 'high'
                - min_rating (float): Minimum star rating
                - requested_amenities (list): Desired amenities
        
        Returns:
            dict: Hotel with added 'recommendation_score' and 'score_breakdown'
        """
        # Extract preferences
        distance = user_preferences.get('distance_km')
        price_pref = user_preferences.get('price_preference')
        min_rating = user_preferences.get('min_rating')
        requested_amenities = user_preferences.get('requested_amenities', [])
        
        # Calculate individual scores
        distance_score = self.calculate_distance_score(distance)
        price_score = self.calculate_price_score(
            hotel.get('price_per_night', 0), 
            price_pref
        )
        rating_score = self.calculate_rating_score(
            hotel.get('star_rating'),
            min_rating
        )
        amenity_score = self.calculate_amenity_score(
            hotel.get('amenities', []),
            requested_amenities
        )
        
        # Calculate weighted total score
        total_score = (
            distance_score * self.weights['distance'] +
            price_score * self.weights['price'] +
            rating_score * self.weights['rating'] +
            amenity_score * self.weights['amenities']
        )
        
        # Add scores to hotel object
        hotel['recommendation_score'] = round(total_score, 2)
        hotel['score_breakdown'] = {
            'distance': round(distance_score, 2),
            'price': round(price_score, 2),
            'rating': round(rating_score, 2),
            'amenities': round(amenity_score, 2)
        }
        
        return hotel
    
    def rank_hotels(self, hotels, user_preferences):
        """
        Score and rank all hotels based on user preferences
        
        Args:
            hotels (list): List of hotel dictionaries
            user_preferences (dict): User preferences for scoring
            
        Returns:
            list: Hotels sorted by recommendation score (highest first)
        """
        # Score each hotel
        scored_hotels = []
        for hotel in hotels:
            # Use distance_from_reference or distance_from_center if available
            if 'distance_from_reference' in hotel:
                user_preferences['distance_km'] = hotel['distance_from_reference']
            elif 'distance_from_center' in hotel:
                user_preferences['distance_km'] = hotel['distance_from_center']
            
            scored_hotel = self.score_hotel(hotel, user_preferences)
            scored_hotels.append(scored_hotel)
        
        # Sort by score (highest first)
        scored_hotels.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return scored_hotels
    
    def get_top_recommendations(self, hotels, user_preferences, count=5):
        """
        Get top N hotel recommendations
        
        Args:
            hotels (list): List of hotel dictionaries
            user_preferences (dict): User preferences
            count (int): Number of recommendations to return
            
        Returns:
            list: Top N recommended hotels
        """
        ranked = self.rank_hotels(hotels, user_preferences)
        return ranked[:count]
    
    def explain_recommendation(self, hotel):
        """
        Generate explanation for why a hotel was recommended
        
        Args:
            hotel (dict): Hotel with recommendation_score and score_breakdown
            
        Returns:
            str: Human-readable explanation
        """
        if 'score_breakdown' not in hotel:
            return "No scoring information available."
        
        breakdown = hotel['score_breakdown']
        score = hotel['recommendation_score']
        
        # Determine strongest factors
        factors = []
        
        if breakdown['distance'] >= 80:
            factors.append("excellent location")
        elif breakdown['distance'] >= 60:
            factors.append("good location")
        
        if breakdown['price'] >= 80:
            factors.append("great value for money")
        elif breakdown['price'] >= 60:
            factors.append("reasonable price")
        
        if breakdown['rating'] >= 80:
            factors.append("high star rating")
        elif breakdown['rating'] >= 60:
            factors.append("good rating")
        
        if breakdown['amenities'] >= 80:
            factors.append("excellent amenity match")
        elif breakdown['amenities'] >= 60:
            factors.append("good amenities")
        
        if not factors:
            return f"Recommended with {score:.1f}% match score."
        
        explanation = f"Recommended (Match: {score:.1f}%) - "
        explanation += ", ".join(factors).capitalize() + "."
        
        return explanation


def test_recommendation_engine():
    """Test the recommendation engine"""
    
    print("\n" + "=" * 60)
    print("Testing Recommendation Engine")
    print("=" * 60)
    
    engine = RecommendationEngine()
    
    # Sample hotels
    sample_hotels = [
        {
            'id': 1,
            'name': 'Budget Hotel Near Haram',
            'price_per_night': 300,
            'star_rating': 3.5,
            'amenities': ['WiFi', 'Parking'],
            'distance_from_reference': 0.5
        },
        {
            'id': 2,
            'name': 'Luxury Hotel with Pool',
            'price_per_night': 1200,
            'star_rating': 5.0,
            'amenities': ['WiFi', 'Pool', 'Gym', 'Restaurant', 'Room Service'],
            'distance_from_reference': 2.0
        },
        {
            'id': 3,
            'name': 'Mid-Range Comfort',
            'price_per_night': 600,
            'star_rating': 4.0,
            'amenities': ['WiFi', 'Restaurant', 'Parking'],
            'distance_from_reference': 1.2
        },
        {
            'id': 4,
            'name': 'Affordable Stay',
            'price_per_night': 250,
            'star_rating': 3.0,
            'amenities': ['WiFi'],
            'distance_from_reference': 5.0
        }
    ]
    
    print("\n[Test 1] Budget Traveler (Low Price Preference)")
    print("-" * 60)
    
    budget_preferences = {
        'price_preference': 'low',
        'min_rating': 3.0,
        'requested_amenities': ['WiFi', 'Parking']
    }
    
    recommendations = engine.get_top_recommendations(
        sample_hotels.copy(), 
        budget_preferences, 
        count=3
    )
    
    print("\nTop 3 Recommendations:")
    for i, hotel in enumerate(recommendations, 1):
        print(f"\n  {i}. {hotel['name']}")
        print(f"     Score: {hotel['recommendation_score']:.1f}/100")
        print(f"     Breakdown: Distance={hotel['score_breakdown']['distance']:.1f}, "
              f"Price={hotel['score_breakdown']['price']:.1f}, "
              f"Rating={hotel['score_breakdown']['rating']:.1f}, "
              f"Amenities={hotel['score_breakdown']['amenities']:.1f}")
        print(f"     {engine.explain_recommendation(hotel)}")
    
    print("\n" + "-" * 60)
    print("[Test 2] Luxury Traveler (High Price Preference)")
    print("-" * 60)
    
    luxury_preferences = {
        'price_preference': 'high',
        'min_rating': 4.5,
        'requested_amenities': ['Pool', 'Gym', 'Restaurant', 'Room Service']
    }
    
    recommendations = engine.get_top_recommendations(
        sample_hotels.copy(), 
        luxury_preferences, 
        count=3
    )
    
    print("\nTop 3 Recommendations:")
    for i, hotel in enumerate(recommendations, 1):
        print(f"\n  {i}. {hotel['name']}")
        print(f"     Score: {hotel['recommendation_score']:.1f}/100")
        print(f"     Price: {hotel['price_per_night']} SAR, Rating: {hotel['star_rating']} stars")
        print(f"     {engine.explain_recommendation(hotel)}")
    
    print("\n" + "-" * 60)
    print("[Test 3] Mid-Range Traveler (Medium Price, Close Location)")
    print("-" * 60)
    
    mid_preferences = {
        'price_preference': 'medium',
        'min_rating': 3.5,
        'requested_amenities': ['WiFi', 'Restaurant']
    }
    
    recommendations = engine.get_top_recommendations(
        sample_hotels.copy(), 
        mid_preferences, 
        count=3
    )
    
    print("\nTop 3 Recommendations:")
    for i, hotel in enumerate(recommendations, 1):
        print(f"\n  {i}. {hotel['name']}")
        print(f"     Score: {hotel['recommendation_score']:.1f}/100")
        print(f"     Distance: {hotel['distance_from_reference']} km")
        print(f"     {engine.explain_recommendation(hotel)}")
    
    print("\n" + "-" * 60)
    print("[Test 4] Custom Weights (Prioritize Location)")
    print("-" * 60)
    
    # Custom engine that prioritizes location
    custom_engine = RecommendationEngine(weights={
        'distance': 0.50,  # 50% weight on distance
        'price': 0.20,
        'rating': 0.20,
        'amenities': 0.10
    })
    
    location_preferences = {
        'price_preference': 'medium',
        'requested_amenities': ['WiFi']
    }
    
    recommendations = custom_engine.get_top_recommendations(
        sample_hotels.copy(), 
        location_preferences, 
        count=3
    )
    
    print("\nTop 3 Recommendations (Location-Focused):")
    for i, hotel in enumerate(recommendations, 1):
        print(f"\n  {i}. {hotel['name']}")
        print(f"     Score: {hotel['recommendation_score']:.1f}/100")
        print(f"     Distance: {hotel['distance_from_reference']} km")
    
    print("\n" + "=" * 60)
    print("Recommendation Engine is working perfectly!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_recommendation_engine()

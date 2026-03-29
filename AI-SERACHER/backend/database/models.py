# Database Models
# Define database models and structures

import json
from datetime import datetime


class Hotel:
    """
    Hotel model representing a hotel entity
    """
    
    def __init__(self, data):
        """
        Initialize Hotel from database row
        
        Args:
            data (dict): Dictionary from database query
        """
        self.id = data.get('id')
        self.name = data.get('name')
        self.address = data.get('address')
        self.city = data.get('city')
        self.country = data.get('country')
        self.latitude = float(data.get('latitude', 0))
        self.longitude = float(data.get('longitude', 0))
        self.description = data.get('description')
        self.star_rating = float(data.get('star_rating', 0))
        
        # Parse JSON amenities
        amenities_str = data.get('amenities', '[]')
        if isinstance(amenities_str, str):
            self.amenities = json.loads(amenities_str)
        else:
            self.amenities = amenities_str
        
        self.price_per_night = float(data.get('price_per_night', 0))
        self.google_place_id = data.get('google_place_id')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    def to_dict(self):
        """
        Convert Hotel object to dictionary
        
        Returns:
            dict: Hotel data as dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude
            },
            'description': self.description,
            'star_rating': self.star_rating,
            'amenities': self.amenities,
            'price_per_night': self.price_per_night,
            'google_place_id': self.google_place_id
        }
    
    def has_amenity(self, amenity):
        """
        Check if hotel has a specific amenity
        
        Args:
            amenity (str): Amenity name
            
        Returns:
            bool: True if hotel has the amenity
        """
        return amenity in self.amenities
    
    def get_coordinates(self):
        """
        Get hotel coordinates as tuple
        
        Returns:
            tuple: (latitude, longitude)
        """
        return (self.latitude, self.longitude)


class Review:
    """
    Review model representing a hotel review
    """
    
    def __init__(self, data):
        """
        Initialize Review from database row
        
        Args:
            data (dict): Dictionary from database query
        """
        self.id = data.get('id')
        self.hotel_id = data.get('hotel_id')
        self.guest_name = data.get('guest_name')
        self.rating = int(data.get('rating', 0))
        self.review_text = data.get('review_text')
        self.sentiment_score = float(data.get('sentiment_score', 0))
        self.created_at = data.get('created_at')
    
    def to_dict(self):
        """
        Convert Review object to dictionary
        
        Returns:
            dict: Review data as dictionary
        """
        return {
            'id': self.id,
            'hotel_id': self.hotel_id,
            'guest_name': self.guest_name,
            'rating': self.rating,
            'review_text': self.review_text,
            'sentiment_score': self.sentiment_score,
            'created_at': str(self.created_at) if self.created_at else None
        }
    
    def is_positive(self):
        """
        Check if review is positive
        
        Returns:
            bool: True if sentiment score is positive
        """
        return self.sentiment_score > 0.1
    
    def is_negative(self):
        """
        Check if review is negative
        
        Returns:
            bool: True if sentiment score is negative
        """
        return self.sentiment_score < -0.1


class Landmark:
    """
    Landmark model representing a landmark location
    """
    
    def __init__(self, data):
        """
        Initialize Landmark from database row
        
        Args:
            data (dict): Dictionary from database query
        """
        self.id = data.get('id')
        self.name = data.get('name')
        
        # Parse JSON alternative names
        alt_names_str = data.get('alternative_names', '[]')
        if isinstance(alt_names_str, str):
            self.alternative_names = json.loads(alt_names_str)
        else:
            self.alternative_names = alt_names_str
        
        self.latitude = float(data.get('latitude', 0))
        self.longitude = float(data.get('longitude', 0))
        self.city = data.get('city')
        self.description = data.get('description')
        self.created_at = data.get('created_at')
    
    def to_dict(self):
        """
        Convert Landmark object to dictionary
        
        Returns:
            dict: Landmark data as dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'alternative_names': self.alternative_names,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude
            },
            'city': self.city,
            'description': self.description
        }
    
    def get_coordinates(self):
        """
        Get landmark coordinates as tuple
        
        Returns:
            tuple: (latitude, longitude)
        """
        return (self.latitude, self.longitude)
    
    def matches_name(self, query):
        """
        Check if query matches landmark name or alternatives
        
        Args:
            query (str): Search query
            
        Returns:
            bool: True if query matches
        """
        query_lower = query.lower()
        
        # Check main name
        if query_lower in self.name.lower():
            return True
        
        # Check alternative names
        for alt_name in self.alternative_names:
            if query_lower in alt_name.lower():
                return True
        
        return False

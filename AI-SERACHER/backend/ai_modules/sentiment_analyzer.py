# Sentiment Analyzer Module
# Analyze hotel reviews and generate summaries

from textblob import TextBlob
from collections import Counter
import re
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SentimentAnalyzer:
    """
    Analyze sentiment of hotel reviews and generate summaries
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer"""
        
        # Positive aspect keywords
        self.positive_aspects = {
            'location': ['location', 'near', 'close', 'proximity', 'walking distance', 'convenient'],
            'cleanliness': ['clean', 'spotless', 'tidy', 'hygienic', 'well-maintained'],
            'staff': ['staff', 'service', 'friendly', 'helpful', 'professional', 'courteous'],
            'comfort': ['comfortable', 'cozy', 'spacious', 'room', 'bed', 'quiet'],
            'amenities': ['amenities', 'facilities', 'pool', 'gym', 'wifi', 'breakfast'],
            'value': ['value', 'price', 'affordable', 'worth', 'reasonable']
        }
        
        # Negative aspect keywords
        self.negative_aspects = {
            'location': ['far', 'distant', 'inconvenient', 'remote'],
            'cleanliness': ['dirty', 'unclean', 'messy', 'unhygienic'],
            'staff': ['rude', 'unhelpful', 'unprofessional', 'slow service'],
            'comfort': ['uncomfortable', 'cramped', 'noisy', 'small', 'old'],
            'amenities': ['broken', 'missing', 'poor facilities', 'no wifi'],
            'value': ['expensive', 'overpriced', 'not worth', 'poor value']
        }
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of a single review
        
        Args:
            text (str): Review text
            
        Returns:
            dict: Sentiment analysis result
        """
        blob = TextBlob(text)
        
        # Get polarity (-1 to 1) and subjectivity (0 to 1)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classify sentiment
        if polarity > 0.1:
            sentiment_label = 'positive'
        elif polarity < -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'polarity': round(polarity, 2),
            'subjectivity': round(subjectivity, 2),
            'label': sentiment_label,
            'text': text
        }
    
    def analyze_reviews(self, reviews):
        """
        Analyze multiple reviews
        
        Args:
            reviews (list): List of review dictionaries with 'review_text' key
            
        Returns:
            dict: Overall sentiment analysis
        """
        if not reviews:
            return {
                'total_reviews': 0,
                'average_polarity': 0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'overall_sentiment': 'neutral'
            }
        
        sentiments = []
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for review in reviews:
            text = review.get('review_text', '')
            if text:
                sentiment = self.analyze_sentiment(text)
                sentiments.append(sentiment)
                sentiment_counts[sentiment['label']] += 1
        
        # Calculate average polarity
        avg_polarity = sum(s['polarity'] for s in sentiments) / len(sentiments)
        
        # Determine overall sentiment
        if avg_polarity > 0.2:
            overall = 'positive'
        elif avg_polarity < -0.2:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'total_reviews': len(reviews),
            'average_polarity': round(avg_polarity, 2),
            'sentiment_distribution': sentiment_counts,
            'overall_sentiment': overall,
            'sentiments': sentiments
        }
    
    def extract_aspects(self, text, sentiment_type='positive'):
        """
        Extract mentioned aspects from review text
        
        Args:
            text (str): Review text
            sentiment_type (str): 'positive' or 'negative'
            
        Returns:
            list: Mentioned aspects
        """
        text_lower = text.lower()
        aspects = []
        
        aspect_dict = self.positive_aspects if sentiment_type == 'positive' else self.negative_aspects
        
        for aspect, keywords in aspect_dict.items():
            for keyword in keywords:
                if keyword in text_lower:
                    aspects.append(aspect)
                    break
        
        return list(set(aspects))  # Remove duplicates
    
    def generate_summary(self, reviews):
        """
        Generate a natural language summary of reviews
        
        Args:
            reviews (list): List of review dictionaries
            
        Returns:
            str: Human-readable summary
        """
        if not reviews:
            return "No reviews available for this hotel."
        
        analysis = self.analyze_reviews(reviews)
        
        # Count positive and negative aspects
        positive_aspects = []
        negative_aspects = []
        
        for review in reviews:
            text = review.get('review_text', '')
            sentiment = self.analyze_sentiment(text)
            
            if sentiment['label'] == 'positive':
                positive_aspects.extend(self.extract_aspects(text, 'positive'))
            elif sentiment['label'] == 'negative':
                negative_aspects.extend(self.extract_aspects(text, 'negative'))
        
        # Count most common aspects
        positive_counter = Counter(positive_aspects)
        negative_counter = Counter(negative_aspects)
        
        # Build summary
        summary_parts = []
        
        # Overall sentiment
        total = analysis['total_reviews']
        pos_count = analysis['sentiment_distribution']['positive']
        neg_count = analysis['sentiment_distribution']['negative']
        
        pos_percent = int((pos_count / total) * 100) if total > 0 else 0
        
        summary_parts.append(f"Based on {total} reviews, {pos_percent}% of guests had a positive experience.")
        
        # Positive aspects
        if positive_counter:
            top_positive = positive_counter.most_common(3)
            aspects_list = [aspect.replace('_', ' ') for aspect, _ in top_positive]
            
            if len(aspects_list) == 1:
                summary_parts.append(f"Guests especially praised the {aspects_list[0]}.")
            elif len(aspects_list) == 2:
                summary_parts.append(f"Guests especially praised the {aspects_list[0]} and {aspects_list[1]}.")
            else:
                summary_parts.append(f"Guests especially praised the {aspects_list[0]}, {aspects_list[1]}, and {aspects_list[2]}.")
        
        # Negative aspects
        if negative_counter and neg_count > 0:
            top_negative = negative_counter.most_common(2)
            aspects_list = [aspect.replace('_', ' ') for aspect, _ in top_negative]
            
            if len(aspects_list) == 1:
                summary_parts.append(f"Some guests had concerns about the {aspects_list[0]}.")
            else:
                summary_parts.append(f"Some guests had concerns about the {aspects_list[0]} and {aspects_list[1]}.")
        
        return " ".join(summary_parts)
    
    def get_sentiment_breakdown(self, reviews):
        """
        Get detailed sentiment breakdown
        
        Args:
            reviews (list): List of review dictionaries
            
        Returns:
            dict: Detailed sentiment breakdown
        """
        analysis = self.analyze_reviews(reviews)
        
        # Extract aspects from all reviews
        all_positive_aspects = []
        all_negative_aspects = []
        
        for review in reviews:
            text = review.get('review_text', '')
            sentiment = self.analyze_sentiment(text)
            
            if sentiment['polarity'] > 0:
                all_positive_aspects.extend(self.extract_aspects(text, 'positive'))
            elif sentiment['polarity'] < 0:
                all_negative_aspects.extend(self.extract_aspects(text, 'negative'))
        
        return {
            'total_reviews': analysis['total_reviews'],
            'average_polarity': analysis['average_polarity'],
            'overall_sentiment': analysis['overall_sentiment'],
            'sentiment_distribution': analysis['sentiment_distribution'],
            'positive_aspects': dict(Counter(all_positive_aspects).most_common(5)),
            'negative_aspects': dict(Counter(all_negative_aspects).most_common(5)),
            'summary': self.generate_summary(reviews)
        }
    
    def compare_hotels(self, hotel_reviews_dict):
        """
        Compare sentiment across multiple hotels
        
        Args:
            hotel_reviews_dict (dict): {hotel_name: [reviews]}
            
        Returns:
            dict: Comparison results
        """
        results = {}
        
        for hotel_name, reviews in hotel_reviews_dict.items():
            analysis = self.analyze_reviews(reviews)
            results[hotel_name] = {
                'average_polarity': analysis['average_polarity'],
                'overall_sentiment': analysis['overall_sentiment'],
                'total_reviews': analysis['total_reviews']
            }
        
        # Sort by average polarity
        sorted_hotels = sorted(results.items(), key=lambda x: x[1]['average_polarity'], reverse=True)
        
        return {
            'rankings': sorted_hotels,
            'details': results
        }


def test_sentiment_analyzer():
    """Test the sentiment analyzer with sample reviews"""
    
    print("\n" + "=" * 60)
    print("Testing Sentiment Analyzer")
    print("=" * 60)
    
    analyzer = SentimentAnalyzer()
    
    # Sample reviews
    sample_reviews = [
        {
            'review_text': 'Excellent hotel! Very clean rooms and the location is perfect. Staff was extremely helpful and friendly.',
            'guest_name': 'Ahmed Ali',
            'rating': 5
        },
        {
            'review_text': 'The view of the Haram from our room was breathtaking. Highly recommend this hotel!',
            'guest_name': 'Fatima Hassan',
            'rating': 5
        },
        {
            'review_text': 'Great hotel overall. The only downside was the breakfast could be better.',
            'guest_name': 'Mohammed Saeed',
            'rating': 4
        },
        {
            'review_text': 'Average experience. Room was okay but service was slow.',
            'guest_name': 'Abdullah Yousef',
            'rating': 3
        },
        {
            'review_text': 'Disappointed with the cleanliness. The room was not well-maintained.',
            'guest_name': 'Sara Ahmed',
            'rating': 2
        }
    ]
    
    print("\n[Test 1] Analyzing Individual Reviews")
    print("-" * 60)
    
    for i, review in enumerate(sample_reviews, 1):
        sentiment = analyzer.analyze_sentiment(review['review_text'])
        print(f"\nReview {i}: \"{review['review_text'][:50]}...\"")
        print(f"  Sentiment: {sentiment['label'].upper()}")
        print(f"  Polarity: {sentiment['polarity']}")
        print(f"  Rating: {review['rating']} stars")
    
    print("\n" + "-" * 60)
    print("[Test 2] Overall Analysis")
    print("-" * 60)
    
    analysis = analyzer.analyze_reviews(sample_reviews)
    print(f"\n✓ Total Reviews: {analysis['total_reviews']}")
    print(f"✓ Average Polarity: {analysis['average_polarity']}")
    print(f"✓ Overall Sentiment: {analysis['overall_sentiment'].upper()}")
    print(f"✓ Distribution:")
    for sentiment, count in analysis['sentiment_distribution'].items():
        print(f"   - {sentiment.capitalize()}: {count}")
    
    print("\n" + "-" * 60)
    print("[Test 3] Review Summary")
    print("-" * 60)
    
    summary = analyzer.generate_summary(sample_reviews)
    print(f"\n{summary}")
    
    print("\n" + "-" * 60)
    print("[Test 4] Detailed Breakdown")
    print("-" * 60)
    
    breakdown = analyzer.get_sentiment_breakdown(sample_reviews)
    print(f"\n✓ Overall Sentiment: {breakdown['overall_sentiment'].upper()}")
    
    if breakdown['positive_aspects']:
        print(f"\n✓ Most Praised Aspects:")
        for aspect, count in breakdown['positive_aspects'].items():
            print(f"   - {aspect.capitalize()}: mentioned {count} times")
    
    if breakdown['negative_aspects']:
        print(f"\n✓ Common Concerns:")
        for aspect, count in breakdown['negative_aspects'].items():
            print(f"   - {aspect.capitalize()}: mentioned {count} times")
    
    print("\n" + "=" * 60)
    print("Sentiment Analyzer is working perfectly!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_sentiment_analyzer()

"""
Test the hotel filtering logic with actual route code
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai_modules.query_parser import QueryParser

# Test 1: Parse "luxury hotels in Riyadh"
qp = QueryParser()
result = qp.parse("luxury hotels in Riyadh")

print("=" * 80)
print("Query Parser Test")
print("=" * 80)
print(f"\nInput: 'luxury hotels in Riyadh'")
print(f"Parsed result:")
print(f"  intent: {result.get('intent')}")
print(f"  city: {result.get('city')}")
print(f"  price_preference: {result.get('price_preference')}")
print(f"  All keys: {list(result.keys())}")

# Test 2: Parse "Show me luxury hotels in Riyadh"
result2 = qp.parse("Show me luxury hotels in Riyadh")
print(f"\nInput: 'Show me luxury hotels in Riyadh'")
print(f"Parsed result:")
print(f"  intent: {result2.get('intent')}")
print(f"  city: {result2.get('city')}")
print(f"  price_preference: {result2.get('price_preference')}")

# Test 3: Just "luxury hotels"
result3 = qp.parse("luxury hotels")
print(f"\nInput: 'luxury hotels'")
print(f"Parsed result:")
print(f"  intent: {result3.get('intent')}")
print(f"  city: {result3.get('city')}")
print(f"  price_preference: {result3.get('price_preference')}")

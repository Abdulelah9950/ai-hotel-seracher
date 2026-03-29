#!/usr/bin/env python3
"""
Quick test to verify MySQL database connection
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from config import DB_CONFIG
from database.db_connection import DatabaseConnection

print("=" * 60)
print("Testing MySQL Database Connection")
print("=" * 60)

print(f"\nConnection Details:")
print(f"  Host: {DB_CONFIG['host']}")
print(f"  Port: {DB_CONFIG['port']}")
print(f"  User: {DB_CONFIG['user']}")
print(f"  Database: {DB_CONFIG['database']}")

# Test connection
db = DatabaseConnection()
print(f"\nAttempting to connect...")

if db.connect():
    print("✅ CONNECTION SUCCESSFUL!")
    
    # Test query
    print("\nTesting basic query...")
    result = db.execute_query("SELECT COUNT(*) as count FROM hotels")
    if result:
        print(f"✅ Query successful!")
        print(f"   Hotels in database: {result[0]['count']}")
    
    # Get all tables
    print("\nTables in database:")
    result = db.execute_query("SHOW TABLES")
    if result:
        for row in result:
            print(f"  - {row[list(row.keys())[0]]}")
    
    db.disconnect()
else:
    print("❌ CONNECTION FAILED!")
    print("\nPossible issues:")
    print("1. MySQL server is not running")
    print("2. Database 'hotel_booking_ai' doesn't exist")
    print("3. Username/password is incorrect")
    print("4. Port is wrong (should be 3306 for XAMPP)")

print("\n" + "=" * 60)

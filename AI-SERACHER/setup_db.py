#!/usr/bin/env python3
"""
Setup MySQL database for Hotel Booking AI
"""
import mysql.connector
from mysql.connector import Error

# Read schema file
with open(r'C:\Users\khale\Documents\GitHub\CS331_Project\database\schema.sql', 'r') as f:
    schema_content = f.read()

# Connection details
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Modtha@7'
}

try:
    # Connect to MySQL
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    
    print("Connected to MySQL successfully!")
    print("Loading schema...")
    
    # Execute schema (split by ; to handle multiple statements)
    statements = schema_content.split(';')
    
    for i, statement in enumerate(statements):
        statement = statement.strip()
        if statement:  # Skip empty statements
            try:
                cursor.execute(statement)
                print(f"✓ Statement {i+1} executed")
            except Error as e:
                print(f"⚠ Statement {i+1}: {e}")
    
    connection.commit()
    print("\n✅ Database setup complete!")
    print("\nDatabase info:")
    
    # Verify tables
    cursor.execute("USE hotel_booking_ai")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"Tables created: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"    Records: {count}")
    
    cursor.close()
    connection.close()
    
except Error as e:
    print(f"❌ Error: {e}")

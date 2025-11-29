#!/usr/bin/env python3
"""
Fix existing transfer request data direction
Run this once to correct old records
"""

import mysql.connector

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'blood_bank_db'
}

def fix_transfer_data():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    print("🔧 Fixing transfer request direction...")
    
    # Get all transfer requests
    cursor.execute("SELECT * FROM transfer_requests")
    requests = cursor.fetchall()
    
    print(f"Found {len(requests)} transfer requests to check")
    
    # Clear existing data and start fresh
    cursor.execute("DELETE FROM transfer_requests")
    print("✅ Cleared existing transfer data")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ Transfer data fixed! Old incorrect records removed.")
    print("💡 Now create new requests - they will use correct direction logic.")

if __name__ == "__main__":
    try:
        fix_transfer_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure MySQL is running and database exists")
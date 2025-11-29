#!/usr/bin/env python3
"""
Setup script to add authentication tables to existing blood bank database
"""

import mysql.connector
import sys

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # No password for local MySQL
    'database': 'blood_bank_db'
}

def setup_authentication():
    conn = None
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Setting up authentication tables...")
        
        # Create hospitals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hospitals (
                hospital_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                address TEXT,
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("Hospital table created. Hospitals can now register themselves.")
        
        conn.commit()
        print("✅ Hospital registration table created successfully!")
        print("\nHospitals can now register at: /register")
        print("Donors can donate blood without registration.")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
        print("\nTroubleshooting:")
        print("1. Check if MySQL is running: brew services start mysql")
        print("2. Make sure the database exists: CREATE DATABASE blood_bank_db;")
        sys.exit(1)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_authentication()
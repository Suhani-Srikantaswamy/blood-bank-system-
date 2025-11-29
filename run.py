#!/usr/bin/env python3
"""
BloodBank Pro - Quick Start Script
Run this file to start the application
"""

import subprocess
import sys
import os

def check_mysql():
    """Check if MySQL is running"""
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='blood_bank_db'
        )
        conn.close()
        print("✅ MySQL connection successful")
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("Please ensure MySQL is running and blood_bank_db exists")
        return False

def main():
    print("🩸 Starting BloodBank Pro...")
    
    # Check MySQL connection
    if not check_mysql():
        print("\n📋 To fix database issues:")
        print("1. Start MySQL: brew services start mysql (macOS)")
        print("2. Create database: mysql -u root -p -e 'CREATE DATABASE blood_bank_db;'")
        print("3. Import schema: mysql -u root -p blood_bank_db < database/schema.sql")
        return
    
    # Start Flask app
    print("🚀 Starting Flask application...")
    print("📱 Open: http://localhost:5000")
    print("🏥 Demo Hospital: admin@citygeneral.com / hospital123")
    print("🩸 Donor Portal: Click 'Donor' on login page")
    
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
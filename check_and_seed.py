#!/usr/bin/env python3
"""
Check existing hospitals and add seed data accordingly
"""

import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'blood_bank_db'
}

def seed_database():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    # Check existing hospitals
    cursor.execute("SELECT hospital_id, name, email FROM hospitals")
    existing_hospitals = cursor.fetchall()
    
    print("🏥 Existing hospitals:")
    for h in existing_hospitals:
        print(f"  ID: {h['hospital_id']}, Name: {h['name']}, Email: {h['email']}")
    
    # Add missing hospitals
    new_hospitals = [
        ('Apollo Hospitals', 'Ahmedabad', 'apollo@gmail.com', '123456', '9876543210'),
        ('Fortis Hospital', 'Mysore', 'fortis@gmail.com', '123456', '9876543212'),
        ('AIIMS Hospital', 'Delhi', 'aiims@gmail.com', '123456', '9876543213'),
        ('Kokilaben Hospital', 'Jaipur', 'kokilaben@gmail.com', '123456', '9876543214'),
        ('Hinduja Hospital', 'Pune', 'hinduja@gmail.com', '123456', '9876543215'),
        ('Narayana Health', 'Kolkata', 'narayana@gmail.com', '123456', '9876543216'),
        ('Rainbow Hospital', 'Hyderabad', 'rainbow@gmail.com', '123456', '9876543217')
    ]
    
    existing_emails = [h['email'] for h in existing_hospitals]
    
    for name, city, email, password, phone in new_hospitals:
        if email not in existing_emails:
            try:
                cursor.execute("""
                    INSERT INTO hospitals (name, city, email, password, phone, reliability_score) 
                    VALUES (%s, %s, %s, %s, %s, 0)
                """, (name, city, email, password, phone))
                print(f"✅ Added hospital: {name}")
            except Exception as e:
                print(f"❌ Failed to add {name}: {e}")
    
    # Add sample donors
    donors = [
        ('Rohan Verma', 28, 'Male', 'A+', '8901234567', 'Ahmedabad'),
        ('Sneha Iyer', 25, 'Female', 'O+', '8901234568', 'Ahmedabad'),
        ('Sujith Kumar', 30, 'Male', 'A+', '8901234572', 'Ranchi'),
        ('Aisha Khan', 27, 'Female', 'O-', '8901234573', 'Ranchi'),
        ('Aman Chopra', 31, 'Male', 'O+', '8901234576', 'Mysore'),
        ('Tania Roy', 28, 'Female', 'B+', '8901234579', 'Delhi'),
        ('Ritika Doshi', 26, 'Female', 'A-', '8901234582', 'Jaipur'),
        ('Sagar Thakur', 29, 'Male', 'B+', '8901234585', 'Pune'),
        ('Rituparna Sen', 28, 'Female', 'O-', '8901234588', 'Kolkata'),
        ('Shiva Reddy', 30, 'Male', 'O+', '8901234591', 'Hyderabad')
    ]
    
    for name, age, gender, blood_group, phone, city in donors:
        try:
            cursor.execute("""
                INSERT INTO donors (name, age, gender, blood_group, phone, city, goodwill_score) 
                VALUES (%s, %s, %s, %s, %s, %s, 0)
            """, (name, age, gender, blood_group, phone, city))
        except Exception as e:
            print(f"❌ Failed to add donor {name}: {e}")
    
    # Get updated hospital list
    cursor.execute("SELECT hospital_id, name FROM hospitals ORDER BY hospital_id")
    all_hospitals = cursor.fetchall()
    
    print(f"\n🏥 All hospitals now:")
    for h in all_hospitals:
        print(f"  ID: {h['hospital_id']}, Name: {h['name']}")
    
    # Add transfer requests using actual hospital IDs
    if len(all_hospitals) >= 3:
        transfers = [
            (all_hospitals[0]['hospital_id'], all_hospitals[1]['hospital_id'], 'A+', 3, 'Approved'),
            (all_hospitals[1]['hospital_id'], all_hospitals[2]['hospital_id'], 'O+', 2, 'Pending'),
            (all_hospitals[2]['hospital_id'], all_hospitals[0]['hospital_id'], 'B+', 1, 'Completed')
        ]
        
        for from_h, to_h, blood_group, units, status in transfers:
            try:
                cursor.execute("""
                    INSERT INTO transfer_requests (from_hospital, to_hospital, blood_group, units_needed, status) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (from_h, to_h, blood_group, units, status))
                print(f"✅ Added transfer: Hospital {from_h} → Hospital {to_h}")
            except Exception as e:
                print(f"❌ Failed to add transfer: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ Seed data completed!")

if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"❌ Error: {e}")

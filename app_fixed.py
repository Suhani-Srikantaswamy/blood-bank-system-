from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'blood_bank_secret_key'

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'database': 'blood_bank_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Dashboard Route
@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get blood group counts
    cursor.execute("""
        SELECT blood_group, COUNT(*) as count 
        FROM blood_inventory 
        WHERE status = 'Available' AND expires_on >= CURDATE()
        GROUP BY blood_group
    """)
    blood_counts = cursor.fetchall()
    
    # Get total donors
    cursor.execute("SELECT COUNT(*) as total FROM donors")
    total_donors = cursor.fetchone()['total']
    
    # Get expired blood bags
    cursor.execute("SELECT COUNT(*) as total FROM blood_inventory WHERE status = 'Expired'")
    expired_bags = cursor.fetchone()['total']
    
    # Get pending emergency requests
    cursor.execute("SELECT COUNT(*) as total FROM emergency_requests WHERE status = 'Pending'")
    pending_requests = cursor.fetchone()['total']
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', 
                         blood_counts=blood_counts,
                         total_donors=total_donors,
                         expired_bags=expired_bags,
                         pending_requests=pending_requests)

# Donor Management Routes
@app.route('/donors')
def donors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM donors ORDER BY donor_id DESC")
    donors_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('donors.html', donors=donors_list)

@app.route('/add_donor', methods=['GET', 'POST'])
def add_donor():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO donors (name, age, gender, blood_group) 
            VALUES (%s, %s, %s, %s)
        """, (name, age, gender, blood_group))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Donor added successfully!', 'success')
        return redirect(url_for('donors'))
    
    return render_template('add_donor.html')

# Blood Inventory Routes
@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT bi.*, d.name as donor_name 
        FROM blood_inventory bi 
        LEFT JOIN donors d ON bi.donor_id = d.donor_id 
        ORDER BY bi.bag_id DESC
    """)
    inventory_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('inventory.html', inventory=inventory_list)

@app.route('/add_blood', methods=['GET', 'POST'])
def add_blood():
    if request.method == 'POST':
        donor_id = request.form['donor_id']
        blood_group = request.form['blood_group']
        collected_on = request.form['collected_on']
        
        # Calculate expiry date (90 days from collection)
        collected_date = datetime.strptime(collected_on, '%Y-%m-%d')
        expires_on = collected_date + timedelta(days=90)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO blood_inventory (donor_id, blood_group, collected_on, expires_on) 
            VALUES (%s, %s, %s, %s)
        """, (donor_id, blood_group, collected_on, expires_on.date()))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Blood bag added successfully!', 'success')
        return redirect(url_for('inventory'))
    
    # Get donors for dropdown
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT donor_id, name, blood_group FROM donors")
    donors_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('add_blood.html', donors=donors_list)

# Emergency Requests Routes
@app.route('/emergency_requests')
def emergency_requests():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM emergency_requests ORDER BY request_id DESC")
    requests_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('emergency_requests.html', requests=requests_list)

@app.route('/add_emergency_request', methods=['GET', 'POST'])
def add_emergency_request():
    if request.method == 'POST':
        requester_name = request.form['requester_name']
        blood_group = request.form['blood_group']
        units_required = request.form['units_required']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emergency_requests (requester_name, blood_group, units_required) 
            VALUES (%s, %s, %s)
        """, (requester_name, blood_group, units_required))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Emergency request submitted successfully!', 'success')
        return redirect(url_for('emergency_requests'))
    
    return render_template('add_emergency_request.html')

@app.route('/approve_request/<int:request_id>')
def approve_request(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE emergency_requests SET status = 'Approved' WHERE request_id = %s", (request_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Emergency request approved!', 'success')
    return redirect(url_for('emergency_requests'))

@app.route('/reject_request/<int:request_id>')
def reject_request(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE emergency_requests SET status = 'Rejected' WHERE request_id = %s", (request_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Emergency request rejected!', 'warning')
    return redirect(url_for('emergency_requests'))

# Logs Route
@app.route('/logs')
def logs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventory_logs ORDER BY log_id DESC LIMIT 100")
    logs_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('logs.html', logs=logs_list)

if __name__ == '__main__':
    app.run(debug=True)
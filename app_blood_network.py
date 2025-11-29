"""
Blood Donation & Hospital Blood Network System
Flask Application with MySQL Backend
Dark Theme UI with Multi-Role Architecture
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from mysql.connector import Error
import bcrypt
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'blood_network_secret_key_2024'

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Empty password
    'database': 'blood_network_db',  # Correct database name
    'autocommit': True
}

# Database Connection Helper
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

# Authentication Decorators
def hospital_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'hospital_id' not in session:
            flash('Please login as hospital to access this page.', 'error')
            return redirect(url_for('hospital_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== PUBLIC ROUTES (DONORS) ====================

@app.route('/')
def index():
    """Public landing page for donors"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Get available hospitals by city
        cursor.execute("SELECT DISTINCT city FROM hospitals ORDER BY city")
        cities = cursor.fetchall()
        
        # Get total blood availability across all hospitals
        cursor.execute("""
            SELECT blood_group, SUM(units_available) as total_units
            FROM hospital_inventory 
            WHERE status = 'Available' AND expiry_date > CURDATE()
            GROUP BY blood_group
            ORDER BY blood_group
        """)
        blood_availability = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('public/donor_home.html', 
                             cities=cities, 
                             blood_availability=blood_availability)
    
    return render_template('public/donor_home.html', cities=[], blood_availability=[])

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    """Donor appointment booking"""
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        age = int(request.form['age'])
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        phone = request.form['phone']
        city = request.form['city']
        hospital_id = int(request.form['hospital_id'])
        preferred_time = request.form['preferred_time']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            try:
                # Check if donor exists
                cursor.execute("SELECT donor_id, last_donation_date FROM donors WHERE phone = %s", (phone,))
                existing_donor = cursor.fetchone()
                
                if existing_donor:
                    donor_id = existing_donor[0]
                    last_donation = existing_donor[1]
                    
                    # Check 90-day rule
                    if last_donation and (datetime.now().date() - last_donation).days < 90:
                        flash(f'You can donate again after {90 - (datetime.now().date() - last_donation).days} days.', 'error')
                        return redirect(url_for('donate'))
                    
                    # Update donor info
                    cursor.execute("""
                        UPDATE donors SET name=%s, age=%s, gender=%s, blood_group=%s, city=%s 
                        WHERE donor_id=%s
                    """, (name, age, gender, blood_group, city, donor_id))
                else:
                    # Create new donor
                    cursor.execute("""
                        INSERT INTO donors (name, age, gender, blood_group, phone, city)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (name, age, gender, blood_group, phone, city))
                    donor_id = cursor.lastrowid
                
                # Create appointment
                cursor.execute("""
                    INSERT INTO donation_appointments (donor_id, hospital_id, preferred_time)
                    VALUES (%s, %s, %s)
                """, (donor_id, hospital_id, preferred_time))
                
                flash('Donation appointment requested successfully! Hospital will contact you soon.', 'success')
                return redirect(url_for('index'))
                
            except Error as e:
                flash(f'Error: {e}', 'error')
            finally:
                cursor.close()
                connection.close()
    
    # GET request - show form
    connection = get_db_connection()
    cities = []
    hospitals = []
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT city FROM hospitals ORDER BY city")
        cities = cursor.fetchall()
        cursor.execute("SELECT hospital_id, hospital_name, city FROM hospitals ORDER BY city, hospital_name")
        hospitals = cursor.fetchall()
        cursor.close()
        connection.close()
    
    return render_template('public/donate.html', cities=cities, hospitals=hospitals)

# ==================== HOSPITAL ROUTES ====================

@app.route('/hospital/login', methods=['GET', 'POST'])
def hospital_login():
    """Hospital login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM hospitals WHERE email = %s", (email,))
            hospital = cursor.fetchone()
            
            if hospital and bcrypt.checkpw(password.encode('utf-8'), hospital['password'].encode('utf-8')):
                session['hospital_id'] = hospital['hospital_id']
                session['hospital_name'] = hospital['hospital_name']
                flash(f'Welcome, {hospital["hospital_name"]}!', 'success')
                return redirect(url_for('hospital_dashboard'))
            else:
                flash('Invalid credentials', 'error')
            
            cursor.close()
            connection.close()
    
    return render_template('hospital/login.html')

@app.route('/hospital/dashboard')
@hospital_required
def hospital_dashboard():
    """Hospital dashboard"""
    hospital_id = session['hospital_id']
    connection = get_db_connection()
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Get hospital inventory
        cursor.execute("""
            SELECT blood_group, SUM(units_available) as total_units
            FROM hospital_inventory 
            WHERE hospital_id = %s AND status = 'Available' AND expiry_date > CURDATE()
            GROUP BY blood_group
            ORDER BY blood_group
        """, (hospital_id,))
        inventory = cursor.fetchall()
        
        # Get pending appointments
        cursor.execute("""
            SELECT da.*, d.name, d.blood_group, d.phone
            FROM donation_appointments da
            JOIN donors d ON da.donor_id = d.donor_id
            WHERE da.hospital_id = %s AND da.status = 'Pending'
            ORDER BY da.created_at DESC
            LIMIT 10
        """, (hospital_id,))
        pending_appointments = cursor.fetchall()
        
        # Get incoming transfer requests
        cursor.execute("""
            SELECT tr.*, h.hospital_name as from_hospital
            FROM transfer_requests tr
            JOIN hospitals h ON tr.from_hospital_id = h.hospital_id
            WHERE tr.to_hospital_id = %s AND tr.status = 'Pending'
            ORDER BY tr.urgency DESC, tr.requested_on DESC
        """, (hospital_id,))
        incoming_requests = cursor.fetchall()
        
        # Get outgoing transfer requests
        cursor.execute("""
            SELECT tr.*, h.hospital_name as to_hospital
            FROM transfer_requests tr
            JOIN hospitals h ON tr.to_hospital_id = h.hospital_id
            WHERE tr.from_hospital_id = %s
            ORDER BY tr.requested_on DESC
            LIMIT 10
        """, (hospital_id,))
        outgoing_requests = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('hospital/dashboard.html',
                             inventory=inventory,
                             pending_appointments=pending_appointments,
                             incoming_requests=incoming_requests,
                             outgoing_requests=outgoing_requests)
    
    return render_template('hospital/dashboard.html')

@app.route('/hospital/inventory')
@hospital_required
def hospital_inventory():
    """Hospital inventory management"""
    hospital_id = session['hospital_id']
    connection = get_db_connection()
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM hospital_inventory 
            WHERE hospital_id = %s 
            ORDER BY blood_group, expiry_date
        """, (hospital_id,))
        inventory = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('hospital/inventory.html', inventory=inventory)
    
    return render_template('hospital/inventory.html', inventory=[])

@app.route('/hospital/add_blood', methods=['GET', 'POST'])
@hospital_required
def add_blood():
    """Add blood to hospital inventory"""
    if request.method == 'POST':
        blood_group = request.form['blood_group']
        units = int(request.form['units'])
        expiry_date = request.form['expiry_date']
        hospital_id = session['hospital_id']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO hospital_inventory (hospital_id, blood_group, units_available, expiry_date)
                    VALUES (%s, %s, %s, %s)
                """, (hospital_id, blood_group, units, expiry_date))
                
                flash('Blood units added successfully!', 'success')
                return redirect(url_for('hospital_inventory'))
                
            except Error as e:
                flash(f'Error: {e}', 'error')
            finally:
                cursor.close()
                connection.close()
    
    return render_template('hospital/add_blood.html')

@app.route('/hospital/appointments')
@hospital_required
def hospital_appointments():
    """Manage donation appointments"""
    hospital_id = session['hospital_id']
    connection = get_db_connection()
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT da.*, d.name, d.age, d.gender, d.blood_group, d.phone, d.city
            FROM donation_appointments da
            JOIN donors d ON da.donor_id = d.donor_id
            WHERE da.hospital_id = %s
            ORDER BY da.created_at DESC
        """, (hospital_id,))
        appointments = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('hospital/appointments.html', appointments=appointments)
    
    return render_template('hospital/appointments.html', appointments=[])

@app.route('/hospital/approve_appointment/<int:appointment_id>')
@hospital_required
def approve_appointment(appointment_id):
    """Approve donation appointment"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE donation_appointments 
            SET status = 'Approved' 
            WHERE appointment_id = %s AND hospital_id = %s
        """, (appointment_id, session['hospital_id']))
        
        flash('Appointment approved successfully!', 'success')
        cursor.close()
        connection.close()
    
    return redirect(url_for('hospital_appointments'))

@app.route('/hospital/complete_appointment/<int:appointment_id>')
@hospital_required
def complete_appointment(appointment_id):
    """Mark appointment as completed"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE donation_appointments 
            SET status = 'Completed' 
            WHERE appointment_id = %s AND hospital_id = %s
        """, (appointment_id, session['hospital_id']))
        
        flash('Donation completed successfully!', 'success')
        cursor.close()
        connection.close()
    
    return redirect(url_for('hospital_appointments'))

@app.route('/hospital/network')
@hospital_required
def hospital_network():
    """View blood availability across all hospitals"""
    connection = get_db_connection()
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT h.hospital_name, h.city, hi.blood_group, 
                   SUM(hi.units_available) as total_units
            FROM hospitals h
            LEFT JOIN hospital_inventory hi ON h.hospital_id = hi.hospital_id
            WHERE hi.status = 'Available' AND hi.expiry_date > CURDATE()
            GROUP BY h.hospital_id, hi.blood_group
            ORDER BY h.city, h.hospital_name, hi.blood_group
        """)
        network_data = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('hospital/network.html', network_data=network_data)
    
    return render_template('hospital/network.html', network_data=[])

@app.route('/hospital/request_blood', methods=['GET', 'POST'])
@hospital_required
def request_blood():
    """Request blood from other hospitals"""
    if request.method == 'POST':
        to_hospital_id = int(request.form['to_hospital_id'])
        blood_group = request.form['blood_group']
        units_needed = int(request.form['units_needed'])
        urgency = request.form['urgency']
        notes = request.form.get('notes', '')
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO transfer_requests 
                    (from_hospital_id, to_hospital_id, blood_group, units_needed, urgency, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (session['hospital_id'], to_hospital_id, blood_group, units_needed, urgency, notes))
                
                flash('Blood transfer request sent successfully!', 'success')
                return redirect(url_for('hospital_dashboard'))
                
            except Error as e:
                flash(f'Error: {e}', 'error')
            finally:
                cursor.close()
                connection.close()
    
    # GET request - show form
    connection = get_db_connection()
    hospitals = []
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT hospital_id, hospital_name, city 
            FROM hospitals 
            WHERE hospital_id != %s
            ORDER BY city, hospital_name
        """, (session['hospital_id'],))
        hospitals = cursor.fetchall()
        
        cursor.close()
        connection.close()
    
    return render_template('hospital/request_blood.html', hospitals=hospitals)

@app.route('/hospital/approve_transfer/<int:request_id>')
@hospital_required
def approve_transfer(request_id):
    """Approve blood transfer request"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE transfer_requests 
            SET status = 'Approved' 
            WHERE request_id = %s AND to_hospital_id = %s
        """, (request_id, session['hospital_id']))
        
        flash('Transfer request approved!', 'success')
        cursor.close()
        connection.close()
    
    return redirect(url_for('hospital_dashboard'))

@app.route('/hospital/deny_transfer/<int:request_id>')
@hospital_required
def deny_transfer(request_id):
    """Deny blood transfer request"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE transfer_requests 
            SET status = 'Denied', resolved_on = CURRENT_TIMESTAMP 
            WHERE request_id = %s AND to_hospital_id = %s
        """, (request_id, session['hospital_id']))
        
        flash('Transfer request denied.', 'info')
        cursor.close()
        connection.close()
    
    return redirect(url_for('hospital_dashboard'))

@app.route('/hospital/logout')
def hospital_logout():
    """Hospital logout"""
    session.pop('hospital_id', None)
    session.pop('hospital_name', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# ==================== ADMIN ROUTES (LIMITED) ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            admin = cursor.fetchone()
            
            if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
                session['admin_id'] = admin['admin_id']
                session['admin_username'] = admin['username']
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid credentials', 'error')
            
            cursor.close()
            connection.close()
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard - limited functionality"""
    connection = get_db_connection()
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # System statistics
        cursor.execute("SELECT COUNT(*) as total_hospitals FROM hospitals")
        total_hospitals = cursor.fetchone()['total_hospitals']
        
        cursor.execute("SELECT COUNT(*) as total_donors FROM donors")
        total_donors = cursor.fetchone()['total_donors']
        
        cursor.execute("SELECT COUNT(*) as pending_appointments FROM donation_appointments WHERE status = 'Pending'")
        pending_appointments = cursor.fetchone()['pending_appointments']
        
        cursor.execute("SELECT COUNT(*) as pending_transfers FROM transfer_requests WHERE status = 'Pending'")
        pending_transfers = cursor.fetchone()['pending_transfers']
        
        cursor.close()
        connection.close()
        
        return render_template('admin/dashboard.html',
                             total_hospitals=total_hospitals,
                             total_donors=total_donors,
                             pending_appointments=pending_appointments,
                             pending_transfers=pending_transfers)
    
    return render_template('admin/dashboard.html')

@app.route('/admin/hospitals')
@admin_required
def admin_hospitals():
    """Manage hospitals"""
    connection = get_db_connection()
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM hospitals ORDER BY city, hospital_name")
        hospitals = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('admin/hospitals.html', hospitals=hospitals)
    
    return render_template('admin/hospitals.html', hospitals=[])

@app.route('/admin/add_hospital', methods=['GET', 'POST'])
@admin_required
def add_hospital():
    """Add new hospital"""
    if request.method == 'POST':
        hospital_name = request.form['hospital_name']
        address = request.form['address']
        city = request.form['city']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO hospitals (hospital_name, address, city, email, password, phone)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (hospital_name, address, city, email, hashed_password, phone))
                
                flash('Hospital registered successfully!', 'success')
                return redirect(url_for('admin_hospitals'))
                
            except Error as e:
                flash(f'Error: {e}', 'error')
            finally:
                cursor.close()
                connection.close()
    
    return render_template('admin/add_hospital.html')

@app.route('/admin/logs')
@admin_required
def admin_logs():
    """View system logs"""
    connection = get_db_connection()
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT sl.*, h.hospital_name
            FROM system_logs sl
            LEFT JOIN hospitals h ON sl.hospital_id = h.hospital_id
            ORDER BY sl.created_at DESC
            LIMIT 100
        """)
        logs = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('admin/logs.html', logs=logs)
    
    return render_template('admin/logs.html', logs=[])

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('index'))

# ==================== API ENDPOINTS ====================

@app.route('/api/hospitals/<city>')
def api_hospitals_by_city(city):
    """API: Get hospitals by city"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT hospital_id, hospital_name FROM hospitals WHERE city = %s", (city,))
        hospitals = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(hospitals)
    return jsonify([])

@app.route('/api/blood_availability/<int:hospital_id>')
def api_blood_availability(hospital_id):
    """API: Get blood availability for specific hospital"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT blood_group, SUM(units_available) as total_units
            FROM hospital_inventory 
            WHERE hospital_id = %s AND status = 'Available' AND expiry_date > CURDATE()
            GROUP BY blood_group
        """, (hospital_id,))
        availability = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(availability)
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import mysql.connector
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'blood_bank_secret_key'

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # No password for local MySQL
    'database': 'blood_bank_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form['user_type']
        
        if user_type == 'donor':
            # Donors go to donor portal
            return redirect(url_for('donor_portal'))
        elif user_type == 'hospital':
            email = request.form['email']
            password = request.form['password']
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM hospitals WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user['hospital_id']
                session['user_type'] = 'hospital'
                session['user_name'] = user['name']
                flash('Login successful!', 'success')
                cursor.close()
                conn.close()
                return redirect(url_for('dashboard'))
            
            cursor.close()
            conn.close()
            flash('Invalid hospital credentials!', 'error')
    
    return render_template('login_premium_unified.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

# Donor Portal Routes
@app.route('/donor', methods=['GET', 'POST'])
def donor_portal():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        gender = request.form['gender']
        phone = request.form['phone']
        city = request.form['city']
        blood_group = request.form['blood_group']
        hospital_id = request.form['hospital_id']
        preferred_time = request.form['preferred_time']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if donor exists
        cursor.execute("SELECT donor_id FROM donors WHERE phone = %s", (phone,))
        existing_donor = cursor.fetchone()
        
        if existing_donor:
            donor_id = existing_donor['donor_id']
        else:
            # Insert new donor
            cursor.execute("""
                INSERT INTO donors (name, age, gender, blood_group, phone, city, goodwill_score) 
                VALUES (%s, %s, %s, %s, %s, %s, 0)
            """, (name, age, gender, blood_group, phone, city))
            donor_id = cursor.lastrowid
            
            # Check for rare blood type
            if blood_group in ['AB-', 'B-', 'O-']:
                cursor.execute("""
                    INSERT INTO rare_donors (donor_id, reason) 
                    VALUES (%s, 'Rare blood type')
                """, (donor_id,))
        
        # Create appointment
        cursor.execute("""
            INSERT INTO donation_appointments (donor_id, hospital_id, preferred_time) 
            VALUES (%s, %s, %s)
        """, (donor_id, hospital_id, preferred_time))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('donation_success', name=name, hospital_id=hospital_id, time=preferred_time))
    
    # GET request - show form
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT city FROM hospitals ORDER BY city")
    cities = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('donor_portal_unified.html', cities=cities)

@app.route('/get_hospitals/<city>')
def get_hospitals(city):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT hospital_id, name FROM hospitals WHERE city = %s", (city,))
    hospitals = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(hospitals)

# Hospital Inventory Management
@app.route('/hospital/inventory', methods=['GET', 'POST'])
@login_required
def hospital_inventory():
    if session.get('user_type') != 'hospital':
        return redirect(url_for('login'))
    
    hospital_id = session.get('user_id')
    
    if request.method == 'POST':
        blood_group = request.form['blood_group']
        units = int(request.form['units'])
        expires_on = request.form['expires_on']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if entry exists
        cursor.execute("""
            SELECT h_bag_id FROM hospital_inventory 
            WHERE hospital_id = %s AND blood_group = %s AND expires_on = %s
        """, (hospital_id, blood_group, expires_on))
        
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE hospital_inventory 
                SET units_available = units_available + %s
                WHERE h_bag_id = %s
            """, (units, existing[0]))
        else:
            cursor.execute("""
                INSERT INTO hospital_inventory (hospital_id, blood_group, units_available, expires_on)
                VALUES (%s, %s, %s, %s)
            """, (hospital_id, blood_group, units, expires_on))
        
        conn.commit()
        cursor.close()
        conn.close()
        flash('Inventory updated successfully!', 'success')
        return redirect(url_for('hospital_inventory'))
    
    # GET request
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT *, 
               created_at as last_updated,
               CASE 
                   WHEN expires_on <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN 'expiring'
                   WHEN units_available < 5 THEN 'low'
                   ELSE 'healthy'
               END as status
        FROM hospital_inventory 
        WHERE hospital_id = %s AND units_available > 0
        ORDER BY blood_group, expires_on
    """, (hospital_id,))
    inventory = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('hospital_inventory_premium.html', inventory=inventory)

@app.route('/hospital/appointments')
@login_required
def hospital_appointments():
    if session.get('user_type') != 'hospital':
        return redirect(url_for('login'))
    
    hospital_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT da.*, d.name, d.blood_group, d.phone, d.city,
               CASE WHEN rd.donor_id IS NOT NULL THEN 1 ELSE 0 END as is_rare_donor
        FROM donation_appointments da
        JOIN donors d ON da.donor_id = d.donor_id
        LEFT JOIN rare_donors rd ON d.donor_id = rd.donor_id
        WHERE da.hospital_id = %s
        ORDER BY da.preferred_time DESC
    """, (hospital_id,))
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('hospital_appointments_premium.html', appointments=appointments)

@app.route('/approve_appointment/<int:appointment_id>')
@login_required
def approve_appointment(appointment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE donation_appointments SET status = 'Approved' WHERE appointment_id = %s", (appointment_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Appointment approved!', 'success')
    return redirect(url_for('hospital_appointments'))

@app.route('/reject_appointment/<int:appointment_id>')
@login_required
def reject_appointment(appointment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE donation_appointments SET status = 'Rejected' WHERE appointment_id = %s", (appointment_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Appointment rejected!', 'warning')
    return redirect(url_for('hospital_appointments'))

@app.route('/donation_success')
def donation_success():
    name = request.args.get('name')
    hospital_id = request.args.get('hospital_id')
    time = request.args.get('time')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name FROM hospitals WHERE hospital_id = %s", (hospital_id,))
    hospital = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('donation_success_premium.html', 
                         donor_name=name, 
                         hospital_name=hospital['name'], 
                         appointment_time=time)

# Hospital Transfer Management
@app.route('/hospital/transfers', methods=['GET', 'POST'])
@login_required
def hospital_transfers():
    if session.get('user_type') != 'hospital':
        return redirect(url_for('login'))
    
    hospital_id = session.get('user_id')
    selected_hospital_id = request.args.get('hospital_id')
    
    if request.method == 'POST':
        blood_group = request.form['blood_group']
        units_needed = int(request.form['units_needed'])
        request_type = request.form['request_type']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request_type == 'all':
            # Send request to all hospitals (current hospital is sender)
            cursor.execute("SELECT hospital_id FROM hospitals WHERE hospital_id != %s", (hospital_id,))
            all_hospitals = cursor.fetchall()
            
            for hospital in all_hospitals:
                cursor.execute("""
                    INSERT INTO transfer_requests (from_hospital, to_hospital, blood_group, units_needed)
                    VALUES (%s, %s, %s, %s)
                """, (hospital_id, hospital['hospital_id'], blood_group, units_needed))
            
            flash(f'Transfer request sent to {len(all_hospitals)} hospitals!', 'success')
        else:
            # Send to selected hospital (current hospital is sender)
            to_hospital = int(request.form['from_hospital'])
            cursor.execute("""
                INSERT INTO transfer_requests (from_hospital, to_hospital, blood_group, units_needed)
                VALUES (%s, %s, %s, %s)
            """, (hospital_id, to_hospital, blood_group, units_needed))
            flash('Transfer request sent!', 'success')
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('hospital_transfers'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get incoming requests
    cursor.execute("""
        SELECT tr.*, h.name as from_hospital_name
        FROM transfer_requests tr
        JOIN hospitals h ON tr.from_hospital = h.hospital_id
        WHERE tr.to_hospital = %s
        ORDER BY tr.created_at DESC
    """, (hospital_id,))
    incoming_requests = cursor.fetchall()
    
    # Get outgoing requests
    cursor.execute("""
        SELECT tr.*, h.name as to_hospital_name
        FROM transfer_requests tr
        JOIN hospitals h ON tr.to_hospital = h.hospital_id
        WHERE tr.from_hospital = %s
        ORDER BY tr.created_at DESC
    """, (hospital_id,))
    outgoing_requests = cursor.fetchall()
    
    # Get other hospitals for request form
    cursor.execute("""
        SELECT hospital_id, name, city FROM hospitals WHERE hospital_id != %s
    """, (hospital_id,))
    other_hospitals = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('hospital_transfers_premium.html', 
                         incoming_requests=incoming_requests,
                         outgoing_requests=outgoing_requests,
                         other_hospitals=other_hospitals,
                         selected_hospital_id=selected_hospital_id)

@app.route('/approve_transfer/<int:request_id>')
@login_required
def approve_transfer(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE transfer_requests SET status = 'Approved' WHERE request_id = %s", (request_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Transfer approved!', 'success')
    return redirect(url_for('hospital_transfers'))

@app.route('/reject_transfer/<int:request_id>')
@login_required
def reject_transfer(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE transfer_requests SET status = 'Rejected' WHERE request_id = %s", (request_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Transfer rejected!', 'warning')
    return redirect(url_for('hospital_transfers'))

@app.route('/hospital/network')
@login_required
def hospital_network():
    if session.get('user_type') != 'hospital':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT h.hospital_id, h.name, h.city, h.reliability_score,
               GROUP_CONCAT(CONCAT(hi.blood_group, ':', hi.units_available) SEPARATOR ', ') as inventory
        FROM hospitals h
        LEFT JOIN hospital_inventory hi ON h.hospital_id = hi.hospital_id AND hi.units_available > 0
        WHERE h.hospital_id != %s
        GROUP BY h.hospital_id
        ORDER BY h.city, h.name
    """, (session.get('user_id'),))
    hospitals = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('hospital_network_premium.html', hospitals=hospitals)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        phone = request.form['phone']
        city = request.form['city']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO hospitals (name, email, password, address, phone, city) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, email, password, address, phone, city))
            conn.commit()
            flash('Hospital registered successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Email already exists!', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register_premium.html')

# Root Route - Redirect to login if not authenticated
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# Hospital Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_type') != 'hospital':
        return redirect(url_for('login'))
    
    hospital_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get inventory summary
    cursor.execute("""
        SELECT blood_group, SUM(units_available) as total_units,
               SUM(CASE WHEN expires_on <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN units_available ELSE 0 END) as expiring_soon
        FROM hospital_inventory 
        WHERE hospital_id = %s AND units_available > 0
        GROUP BY blood_group
    """, (hospital_id,))
    inventory_summary = cursor.fetchall()
    
    # Calculate Blood Urgency Index (BUI)
    cursor.execute("""
        SELECT tr.blood_group, 
               SUM(tr.units_needed) as requested_units,
               COALESCE(hi.total_units, 0) as available_units,
               COALESCE(hi.expiring_soon, 0) as expiring_soon
        FROM transfer_requests tr
        LEFT JOIN (
            SELECT blood_group, SUM(units_available) as total_units,
                   SUM(CASE WHEN expires_on <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN units_available ELSE 0 END) as expiring_soon
            FROM hospital_inventory WHERE hospital_id = %s GROUP BY blood_group
        ) hi ON tr.blood_group = hi.blood_group
        WHERE tr.to_hospital = %s AND tr.status = 'Pending'
        GROUP BY tr.blood_group
    """, (hospital_id, hospital_id))
    bui_data = cursor.fetchall()
    
    # Get pending appointments
    cursor.execute("""
        SELECT COUNT(*) as pending_appointments
        FROM donation_appointments 
        WHERE hospital_id = %s AND status = 'Pending'
    """, (hospital_id,))
    pending_appointments = cursor.fetchone()['pending_appointments']
    
    # Get today's appointments
    cursor.execute("""
        SELECT COUNT(*) as today_appointments
        FROM donation_appointments 
        WHERE hospital_id = %s AND DATE(preferred_time) = CURDATE()
    """, (hospital_id,))
    today_appointments = cursor.fetchone()['today_appointments']
    
    # Get transfer requests
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM transfer_requests WHERE to_hospital = %s AND status = 'Pending') as incoming_requests,
            (SELECT COUNT(*) FROM transfer_requests WHERE from_hospital = %s AND status = 'Pending') as outgoing_requests
    """, (hospital_id, hospital_id))
    transfer_summary = cursor.fetchone()
    
    # Get rare donors in city
    cursor.execute("""
        SELECT city FROM hospitals WHERE hospital_id = %s
    """, (hospital_id,))
    hospital_result = cursor.fetchone()
    hospital_city = hospital_result['city'] if hospital_result else 'Unknown'
    
    cursor.execute("""
        SELECT d.name, d.blood_group, d.phone
        FROM donors d
        JOIN rare_donors rd ON d.donor_id = rd.donor_id
        WHERE d.city = %s
        ORDER BY d.name
    """, (hospital_city,))
    rare_donors = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('hospital_dashboard_premium.html', 
                         inventory_summary=inventory_summary,
                         bui_data=bui_data,
                         pending_appointments=pending_appointments,
                         today_appointments=today_appointments,
                         transfer_summary=transfer_summary,
                         rare_donors=rare_donors)

# Original Dashboard Route (fallback)
@app.route('/old_dashboard')
@login_required
def old_dashboard():
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
@login_required
def donors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM donors ORDER BY donor_id DESC")
    donors_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('donors.html', donors=donors_list)

@app.route('/add_donor', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
def emergency_requests():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT er.*, h.name as hospital_name 
        FROM emergency_requests er 
        LEFT JOIN hospitals h ON er.hospital_id = h.hospital_id 
        ORDER BY 
            CASE er.urgency 
                WHEN 'Critical' THEN 1 
                WHEN 'High' THEN 2 
                WHEN 'Medium' THEN 3 
                WHEN 'Low' THEN 4 
            END, 
            er.requested_on DESC
    """)
    requests_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('emergency_requests.html', requests=requests_list)

@app.route('/add_emergency_request', methods=['GET', 'POST'])
@login_required
def add_emergency_request():
    if request.method == 'POST':
        requester_name = request.form['requester_name']
        blood_group = request.form['blood_group']
        units_required = request.form['units_required']
        urgency = request.form['urgency']
        
        hospital_id = session.get('user_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emergency_requests (hospital_id, requester_name, blood_group, units_required, urgency) 
            VALUES (%s, %s, %s, %s, %s)
        """, (hospital_id, requester_name, blood_group, units_required, urgency))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Emergency request submitted successfully!', 'success')
        return redirect(url_for('emergency_requests'))
    
    return render_template('add_emergency_request.html')

@app.route('/approve_request/<int:request_id>')
@login_required
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
@login_required
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
@login_required
def logs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventory_logs ORDER BY log_id DESC LIMIT 100")
    logs_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('logs.html', logs=logs_list)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
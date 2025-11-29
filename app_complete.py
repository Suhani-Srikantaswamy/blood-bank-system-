from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from datetime import datetime, timedelta
from functools import wraps
import hashlib

app = Flask(__name__)
app.secret_key = 'blood_bank_professional_secret_key_2025'

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'database': 'blood_bank_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hashlib.sha256(password.encode()).hexdigest() == hashed

# Authentication decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def hospital_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if user_type == 'admin' and email == 'admin@bloodbank.com':
            cursor.execute("SELECT * FROM hospitals WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user and password == 'admin123':
                session['user_id'] = user['hospital_id']
                session['user_name'] = 'System Admin'
                session['user_type'] = 'admin'
                cursor.close()
                conn.close()
                return redirect(url_for('admin_dashboard'))
        
        elif user_type == 'hospital':
            cursor.execute("SELECT * FROM hospitals WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user and password == 'hospital123':
                session['user_id'] = user['hospital_id']
                session['user_name'] = user['hospital_name']
                session['user_type'] = 'hospital'
                cursor.close()
                conn.close()
                return redirect(url_for('hospital_dashboard'))
        
        cursor.close()
        conn.close()
        flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hospital_name = request.form['hospital_name']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO hospitals (hospital_name, email, password) 
                VALUES (%s, %s, %s)
            """, (hospital_name, email, hash_password(password)))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Email already exists', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

# Admin Dashboard Routes
@app.route('/')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT blood_group, COUNT(*) as count FROM blood_inventory WHERE status = 'Available' AND expires_on >= CURDATE() GROUP BY blood_group")
    blood_counts = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) as total FROM donors")
    total_donors = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM blood_inventory WHERE status = 'Expired'")
    expired_bags = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM emergency_requests WHERE status = 'Pending'")
    pending_requests = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM hospitals WHERE hospital_id != 1")
    total_hospitals = cursor.fetchone()['total']
    
    cursor.execute("SELECT * FROM inventory_logs ORDER BY log_id DESC LIMIT 5")
    recent_logs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         blood_counts=blood_counts,
                         total_donors=total_donors,
                         expired_bags=expired_bags,
                         pending_requests=pending_requests,
                         total_hospitals=total_hospitals,
                         recent_logs=recent_logs)

@app.route('/admin/donors')
@admin_required
def admin_donors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM donors ORDER BY donor_id DESC")
    donors_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/donors.html', donors=donors_list)

@app.route('/admin/add_donor', methods=['GET', 'POST'])
@admin_required
def add_donor():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        phone = request.form['phone']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO donors (name, age, gender, blood_group, phone) 
            VALUES (%s, %s, %s, %s, %s)
        """, (name, age, gender, blood_group, phone))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Donor added successfully!', 'success')
        return redirect(url_for('admin_donors'))
    
    return render_template('admin/add_donor.html')

@app.route('/admin/inventory')
@admin_required
def admin_inventory():
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
    return render_template('admin/inventory.html', inventory=inventory_list)

@app.route('/admin/add_blood', methods=['GET', 'POST'])
@admin_required
def add_blood():
    if request.method == 'POST':
        donor_id = request.form['donor_id']
        blood_group = request.form['blood_group']
        collected_on = request.form['collected_on']
        
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
        return redirect(url_for('admin_inventory'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT donor_id, name, blood_group FROM donors")
    donors_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin/add_blood.html', donors=donors_list)

@app.route('/admin/emergency_requests')
@admin_required
def admin_emergency_requests():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT er.*, h.hospital_name 
        FROM emergency_requests er 
        LEFT JOIN hospitals h ON er.hospital_id = h.hospital_id 
        ORDER BY er.request_id DESC
    """)
    requests_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/emergency_requests.html', requests=requests_list)

@app.route('/admin/approve_request/<int:request_id>')
@admin_required
def approve_request(request_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM emergency_requests WHERE request_id = %s", (request_id,))
    request_data = cursor.fetchone()
    
    if request_data:
        cursor.execute("UPDATE emergency_requests SET status = 'Approved', approved_on = NOW() WHERE request_id = %s", (request_id,))
        
        cursor.execute("""
            UPDATE blood_inventory 
            SET status = 'Used' 
            WHERE blood_group = %s AND status = 'Available' AND expires_on >= CURDATE()
            ORDER BY expires_on ASC
            LIMIT %s
        """, (request_data['blood_group'], request_data['units_required']))
        
        conn.commit()
        flash('Emergency request approved successfully!', 'success')
    
    cursor.close()
    conn.close()
    return redirect(url_for('admin_emergency_requests'))

@app.route('/admin/reject_request/<int:request_id>')
@admin_required
def reject_request(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE emergency_requests SET status = 'Rejected' WHERE request_id = %s", (request_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Emergency request rejected!', 'warning')
    return redirect(url_for('admin_emergency_requests'))

# Hospital Dashboard Routes
@app.route('/hospital/dashboard')
@hospital_required
def hospital_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM emergency_requests 
        WHERE hospital_id = %s 
        ORDER BY request_id DESC LIMIT 10
    """, (session['user_id'],))
    my_requests = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) as total FROM emergency_requests WHERE hospital_id = %s", (session['user_id'],))
    total_requests = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as pending FROM emergency_requests WHERE hospital_id = %s AND status = 'Pending'", (session['user_id'],))
    pending_requests = cursor.fetchone()['pending']
    
    cursor.execute("SELECT COUNT(*) as approved FROM emergency_requests WHERE hospital_id = %s AND status = 'Approved'", (session['user_id'],))
    approved_requests = cursor.fetchone()['approved']
    
    cursor.close()
    conn.close()
    
    return render_template('hospital/dashboard.html',
                         my_requests=my_requests,
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         approved_requests=approved_requests)

@app.route('/hospital/request_blood', methods=['GET', 'POST'])
@hospital_required
def request_blood():
    if request.method == 'POST':
        blood_group = request.form['blood_group']
        units_required = request.form['units_required']
        urgency = request.form['urgency']
        notes = request.form['notes']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emergency_requests (hospital_id, requester_name, blood_group, units_required, urgency, notes) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session['user_id'], session['user_name'], blood_group, units_required, urgency, notes))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Blood request submitted successfully!', 'success')
        return redirect(url_for('hospital_dashboard'))
    
    return render_template('hospital/request_blood.html')

if __name__ == '__main__':
    app.run(debug=True)
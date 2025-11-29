# Blood Donation & Hospital Blood Network System
## Complete Setup Instructions

### 🩸 System Overview
A comprehensive dark-themed blood network system with:
- **Public Donors**: No login required, book appointments
- **Hospital Login**: Manage inventory, approve donations, transfer blood
- **Admin Login**: Limited role - only hospital management and monitoring

---

## 📋 Prerequisites
- Python 3.8+
- MySQL 8.0+
- Web browser (Chrome, Firefox, Safari)

---

## 🚀 Installation Steps

### Step 1: Install MySQL
```bash
# macOS (using Homebrew)
brew install mysql
brew services start mysql

# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql

# Windows
# Download from https://dev.mysql.com/downloads/mysql/
```

### Step 2: Setup Database
```bash
# Login to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE blood_network_db;
CREATE USER 'bloodnetwork_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON blood_network_db.* TO 'bloodnetwork_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Import Database Schema
```bash
# Import schema, triggers, and sample data
mysql -u root -p blood_network_db < database/blood_network_schema.sql
mysql -u root -p blood_network_db < database/blood_network_triggers.sql
```

### Step 4: Install Python Dependencies
```bash
# Create virtual environment
python -m venv blood_network_env
source blood_network_env/bin/activate  # On Windows: blood_network_env\Scripts\activate

# Install requirements
pip install -r requirements_blood_network.txt
```

### Step 5: Configure Database Connection
Edit `app_blood_network.py` and update:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'bloodnetwork_user',  # or 'root'
    'password': 'your_password',  # Update this
    'database': 'blood_network_db',
    'autocommit': True
}
```

### Step 6: Run the Application
```bash
python app_blood_network.py
```

Visit `http://localhost:5000` in your browser.

---

## 🔐 Demo Login Credentials

### Hospital Accounts
1. **City General Hospital**
   - Email: `admin@citygeneral.com`
   - Password: `hospital123`

2. **Metro Medical Center**
   - Email: `contact@metromedical.com`
   - Password: `hospital123`

3. **Regional Blood Bank**
   - Email: `info@regionalblood.com`
   - Password: `hospital123`

### Admin Account
- Username: `admin`
- Password: `admin123`

---

## 🏗️ System Architecture

### Multi-Role Design
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PUBLIC USER   │    │    HOSPITAL     │    │     ADMIN       │
│   (No Login)    │    │    (Login)      │    │   (Limited)     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Book donation │    │ • Manage stock  │    │ • Add hospitals │
│ • View hospitals│    │ • Approve donors│    │ • View logs     │
│ • Check blood   │    │ • Transfer blood│    │ • Monitor only  │
│   availability  │    │ • Emergency req │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Database Tables
- `donors` - Public donor information
- `hospitals` - Hospital accounts and details
- `donation_appointments` - Donor appointment requests
- `hospital_inventory` - Blood stock per hospital
- `transfer_requests` - Hospital-to-hospital requests
- `system_logs` - Complete audit trail
- `admins` - Limited admin accounts

---

## 🎨 Dark Theme Features
- Deep red, charcoal, navy color scheme
- Responsive Bootstrap 5 design
- Card-based layout with shadows
- Hover effects and animations
- Mobile-friendly interface

---

## 🔄 Workflow Examples

### 1. Donor Appointment Flow
```
Donor visits homepage → Fills form → Selects hospital → Books appointment
→ Hospital receives request → Hospital approves → Donor gets contacted
→ Donation completed → Blood added to inventory
```

### 2. Emergency Blood Transfer
```
Hospital A needs O- blood → Checks network availability → Requests from Hospital B
→ Hospital B approves → Blood transferred automatically → Inventory updated
→ All actions logged
```

### 3. Admin Hospital Management
```
Admin logs in → Views hospital list → Adds new hospital → Hospital can login
→ Admin monitors logs → Views system statistics
```

---

## 🛠️ API Endpoints

### Public Routes
- `GET /` - Homepage with blood availability
- `GET /donate` - Donation form
- `POST /donate` - Submit appointment

### Hospital Routes
- `POST /hospital/login` - Hospital authentication
- `GET /hospital/dashboard` - Main dashboard
- `GET /hospital/inventory` - Blood inventory
- `POST /hospital/add_blood` - Add blood units
- `GET /hospital/network` - View all hospitals
- `POST /hospital/request_blood` - Request transfer

### Admin Routes
- `POST /admin/login` - Admin authentication
- `GET /admin/dashboard` - System overview
- `GET /admin/hospitals` - Hospital management
- `POST /admin/add_hospital` - Register hospital

### API Endpoints
- `GET /api/hospitals/<city>` - Hospitals by city
- `GET /api/blood_availability/<hospital_id>` - Blood stock

---

## 🔧 MySQL Triggers

### Automated Features
1. **Auto-expire blood** - Updates status when expiry date passes
2. **Auto-log actions** - Records all blood additions
3. **Auto-transfer** - Handles approved transfer requests
4. **Auto-update donors** - Updates last donation date
5. **Daily cleanup** - Expires old blood units

---

## 📊 System Features

### ✅ Implemented Features
- [x] Public donor registration (no login)
- [x] Hospital-to-hospital blood network
- [x] Real-time inventory management
- [x] Emergency blood requests
- [x] Automated expiry management
- [x] Complete audit logging
- [x] Dark theme UI
- [x] Mobile responsive design
- [x] Form validation
- [x] MySQL triggers
- [x] Multi-role authentication

### 🚫 Admin Limitations (By Design)
- ❌ Cannot approve blood transfers
- ❌ Cannot add blood inventory
- ❌ Cannot handle donations
- ❌ Cannot manage emergencies

---

## 🧪 Testing the System

### Test Scenario 1: Donor Appointment
1. Visit homepage
2. Click "Donate Blood Now"
3. Fill form with valid data
4. Select city and hospital
5. Book appointment
6. Login as hospital
7. Approve appointment

### Test Scenario 2: Blood Transfer
1. Login as Hospital A
2. Go to "Request Blood"
3. Select Hospital B and blood type
4. Submit request
5. Login as Hospital B
6. Approve transfer request
7. Check inventory updates

### Test Scenario 3: Admin Management
1. Login as admin
2. View system statistics
3. Add new hospital
4. Check system logs
5. Monitor hospital activities

---

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection Error**
   - Check MySQL is running
   - Verify credentials in `app_blood_network.py`
   - Ensure database exists

2. **Import Error**
   - Activate virtual environment
   - Install requirements: `pip install -r requirements_blood_network.txt`

3. **Template Not Found**
   - Ensure all template directories exist
   - Check file paths in Flask routes

4. **Login Issues**
   - Use provided demo credentials
   - Check password hashing in database

---

## 📈 Production Deployment

### Security Enhancements
- Change default passwords
- Use environment variables for secrets
- Enable HTTPS
- Add rate limiting
- Implement CSRF protection

### Performance Optimization
- Add database indexing
- Implement caching
- Use connection pooling
- Add monitoring

---

## 🎓 Viva Questions & Answers

### Q1: Why is admin role limited?
**A:** To ensure real-time hospital-to-hospital communication without administrative bottlenecks during emergencies.

### Q2: How does the 90-day donation rule work?
**A:** System checks `last_donation_date` in donors table and prevents booking if less than 90 days have passed.

### Q3: What happens when blood expires?
**A:** MySQL triggers automatically update status to 'Expired' and log the action.

### Q4: How are transfer requests handled?
**A:** Hospitals request directly from each other. Approval triggers automatic inventory updates.

### Q5: Why no login for donors?
**A:** Reduces barriers to donation while maintaining contact information for emergencies.

---

## 📞 Support
For issues or questions, check the system logs in admin panel or review the database triggers for automated processes.

**System Status**: ✅ Production Ready
**Last Updated**: 2024
**Version**: 1.0.0
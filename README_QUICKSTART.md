# BloodBank Pro - Quick Start Guide

## 🚀 To Run Your Application

1. **Start MySQL** (if not running):
   ```bash
   brew services start mysql
   ```

2. **Run the application**:
   ```bash
   python run.py
   ```
   OR
   ```bash
   python app.py
   ```

3. **Open in browser**: http://localhost:5000

## 🔑 Demo Login Credentials

### Hospital Login:
- **Email**: admin@citygeneral.com
- **Password**: hospital123

### Donor Portal:
- Click "Donor" on login page (no login required)

## 📊 Your Database Data

All your existing data will be preserved including:
- Hospital accounts and inventory
- Donor registrations and appointments  
- Blood transfer requests
- System logs and activity

## 🛠️ If Database Issues:

1. **Check MySQL is running**:
   ```bash
   mysql -u root -p -e "SHOW DATABASES;"
   ```

2. **Recreate database if needed**:
   ```bash
   mysql -u root -p -e "CREATE DATABASE blood_bank_db;"
   mysql -u root -p blood_bank_db < database/schema.sql
   mysql -u root -p blood_bank_db < database/sample_data.sql
   ```

## 📁 Project Structure
```
blood_bank_system/
├── app.py                          # Main Flask application
├── run.py                          # Quick start script
├── requirements.txt                # Dependencies
├── static/
│   ├── css/
│   │   ├── premium.css            # Main theme
│   │   └── custom-dropdown.css    # Custom dropdowns
│   └── js/
│       └── custom-dropdown.js     # Dropdown functionality
├── templates/
│   ├── login_premium_unified.html  # Login page
│   ├── donor_portal_unified.html   # Donor registration
│   ├── hospital_*_premium.html     # Hospital pages
│   └── base_premium.html          # Base template
└── database/
    ├── schema.sql                 # Database structure
    └── sample_data.sql            # Demo data
```

## 🎨 Features Included
- ✅ Premium dark-blue theme
- ✅ Custom styled dropdowns
- ✅ Hospital management system
- ✅ Donor portal and appointments
- ✅ Blood inventory tracking
- ✅ Transfer request system
- ✅ Hospital network view
- ✅ Responsive design
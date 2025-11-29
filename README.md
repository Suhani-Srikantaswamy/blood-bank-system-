# Blood Bank & Emergency Availability Monitoring System

A comprehensive web application built with Flask and MySQL for managing blood bank operations, donor information, inventory tracking, and emergency requests.

## Features

- **Dashboard**: Real-time overview of blood availability, donors, and emergency requests
- **Donor Management**: Add, view, and track donor eligibility (90-day rule)
- **Blood Inventory**: Track blood bags with automatic expiry management
- **Emergency Requests**: Handle urgent blood requests with approval workflow
- **System Logs**: Complete audit trail of all system activities
- **Automated Triggers**: MySQL triggers for expiry, logging, and inventory management

## Installation & Setup

### Prerequisites
- Python 3.7+
- MySQL 8.0+
- pip (Python package manager)

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
# Download and install from https://dev.mysql.com/downloads/mysql/
```

### Step 2: Setup Database
```bash
# Login to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE blood_bank_db;
CREATE USER 'bloodbank_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON blood_bank_db.* TO 'bloodbank_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Import Database Schema
```bash
# Import schema and triggers
mysql -u root -p blood_bank_db < database/schema.sql
mysql -u root -p blood_bank_db < database/triggers.sql
mysql -u root -p blood_bank_db < database/sample_data.sql

# Setup authentication (adds user tables and demo accounts)
python setup_auth.py
```

### Step 4: Install Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 5: Configure Database Connection
Edit `app.py` and update the database configuration:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'bloodbank_user',  # or 'root'
    'password': 'your_password',
    'database': 'blood_bank_db'
}
```

### Step 6: Run the Application
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Project Structure
```
blood_bank_system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── database/
│   ├── schema.sql        # Database tables
│   ├── triggers.sql      # MySQL triggers
│   └── sample_data.sql   # Sample data
├── templates/            # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── donors.html
│   ├── add_donor.html
│   ├── inventory.html
│   ├── add_blood.html
│   ├── emergency_requests.html
│   ├── add_emergency_request.html
│   └── logs.html
└── static/
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        └── script.js     # JavaScript functionality
```

## Usage

### Demo Login Credentials
- **Admin**: admin@bloodbank.com / admin123
- **Hospital**: admin@citygeneral.com / hospital123
- **Hospital**: contact@metromedical.com / hospital123
- **Hospital**: info@regionalblood.com / hospital123

### Features
1. **Dashboard**: View system overview and statistics
2. **Add Donors**: Register new blood donors
3. **Manage Inventory**: Add blood bags and track expiry
4. **Emergency Requests**: Submit and approve urgent requests
5. **View Logs**: Monitor all system activities
6. **User Authentication**: Login system for admins and hospitals
7. **Hospital Registration**: New hospitals can register themselves

## Database Schema

### Tables
- `donors`: Donor information and eligibility tracking
- `blood_inventory`: Blood bag inventory with expiry management
- `emergency_requests`: Emergency blood requests workflow
- `inventory_logs`: System activity audit trail
- `admin_users`: System administrator accounts
- `hospitals`: Hospital user accounts with registration info

### Triggers
- Auto-expire blood bags past expiry date
- Log new blood bag additions
- Handle emergency request approvals
- Update donor last donation dates

## Technologies Used
- **Backend**: Python Flask
- **Database**: MySQL 8.0
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Features**: MySQL Triggers, Responsive Design, Form Validation
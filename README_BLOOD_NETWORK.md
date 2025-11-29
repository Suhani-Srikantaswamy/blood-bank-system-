# 🩸 Blood Donation & Hospital Blood Network System

## 🌟 Complete Dark-Themed Multi-Role Blood Management System

A comprehensive web application built with **Flask + MySQL** featuring a modern dark UI and multi-role architecture for managing blood donations, hospital inventory, and emergency transfers.

---

## 🎯 System Overview

### **Three-Role Architecture**

#### 1. 👥 **Public Donors** (No Login Required)
- Book donation appointments
- Select nearest hospitals
- View blood availability
- Receive appointment confirmations
- Tracked for future donations (90-day rule)

#### 2. 🏥 **Hospital Users** (Login Required)
- Manage blood inventory
- Approve/reject donor appointments
- Request blood from other hospitals
- Approve/deny transfer requests
- View network-wide blood availability
- Real-time emergency communication

#### 3. 🛡️ **Admin Users** (Limited Role)
- Register new hospitals
- Monitor system logs
- View analytics
- **Cannot** interfere with blood operations
- **Cannot** approve transfers or handle emergencies

---

## 🗄️ Database Schema

### **Core Tables**
```sql
donors                    -- Public donor information
hospitals                 -- Hospital accounts & details
donation_appointments     -- Donor appointment requests
hospital_inventory        -- Blood stock per hospital
transfer_requests         -- Hospital-to-hospital requests
system_logs              -- Complete audit trail
admins                   -- Limited admin accounts
```

### **Key Features**
- ✅ Automated blood expiry management
- ✅ 90-day donation rule enforcement
- ✅ Real-time inventory updates
- ✅ Complete audit logging
- ✅ Emergency transfer protocols

---

## 🎨 Dark Theme UI

### **Design Elements**
- **Color Scheme**: Deep red, charcoal, navy, slate
- **Components**: Cards with shadows & rounded corners
- **Tables**: Dark striped with hover effects
- **Forms**: Comprehensive validation
- **Responsive**: Mobile-friendly Bootstrap 5

### **Visual Features**
- Blood group badges
- Urgency indicators with animations
- Real-time clock
- Loading states
- Smooth transitions

---

## 🚀 Quick Start

### **1. Database Setup**
```bash
mysql -u root -p
CREATE DATABASE blood_network_db;
mysql -u root -p blood_network_db < database/blood_network_schema.sql
mysql -u root -p blood_network_db < database/blood_network_triggers.sql
```

### **2. Install Dependencies**
```bash
python -m venv blood_network_env
source blood_network_env/bin/activate
pip install -r requirements_blood_network.txt
```

### **3. Configure & Run**
```bash
# Update database credentials in app_blood_network.py
python app_blood_network.py
# Visit http://localhost:5000
```

---

## 🔐 Demo Credentials

### **Hospital Logins**
| Hospital | Email | Password |
|----------|-------|----------|
| City General Hospital | admin@citygeneral.com | hospital123 |
| Metro Medical Center | contact@metromedical.com | hospital123 |
| Regional Blood Bank | info@regionalblood.com | hospital123 |

### **Admin Login**
- **Username**: admin
- **Password**: admin123

---

## 📋 File Structure

```
blood_bank_system/
├── app_blood_network.py          # Main Flask application
├── requirements_blood_network.txt # Python dependencies
├── database/
│   ├── blood_network_schema.sql   # Database tables & sample data
│   └── blood_network_triggers.sql # MySQL triggers
├── static/
│   ├── css/dark_theme.css         # Dark theme styles
│   └── js/blood_network.js        # JavaScript functionality
├── templates/
│   ├── base_dark.html             # Base template
│   ├── public/                    # Donor pages
│   │   ├── donor_home.html
│   │   └── donate.html
│   ├── hospital/                  # Hospital pages
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── inventory.html
│   │   ├── add_blood.html
│   │   ├── appointments.html
│   │   ├── network.html
│   │   └── request_blood.html
│   └── admin/                     # Admin pages
│       ├── login.html
│       ├── dashboard.html
│       ├── hospitals.html
│       ├── add_hospital.html
│       └── logs.html
├── ER_DIAGRAM.md                  # Database design
├── SETUP_INSTRUCTIONS.md          # Detailed setup guide
└── README_BLOOD_NETWORK.md        # This file
```

---

## 🔄 System Workflows

### **Donor Appointment Flow**
```
1. Donor visits homepage
2. Fills donation form
3. Selects city & hospital
4. Books appointment
5. Hospital receives request
6. Hospital approves/rejects
7. Donation completed
8. Blood added to inventory
```

### **Emergency Blood Transfer**
```
1. Hospital A needs blood urgently
2. Views network availability
3. Requests from Hospital B
4. Hospital B approves transfer
5. Inventory automatically updated
6. All actions logged
```

### **Admin Hospital Management**
```
1. Admin registers new hospital
2. Hospital receives login credentials
3. Hospital joins blood network
4. Admin monitors system logs
5. Analytics and reporting
```

---

## 🛠️ Technical Features

### **Backend (Flask)**
- Blueprint-based architecture
- Session management
- Input validation
- MySQL integration
- RESTful API endpoints

### **Frontend (HTML/CSS/JS)**
- Bootstrap 5 responsive design
- Dark theme implementation
- Form validation
- Real-time updates
- Mobile optimization

### **Database (MySQL)**
- Normalized schema design
- Automated triggers
- Foreign key constraints
- Indexing for performance
- Event scheduling

---

## 🔧 MySQL Triggers

### **Automated Processes**
1. **Blood Expiry**: Auto-expire units past expiry date
2. **Action Logging**: Log all blood additions and transfers
3. **Inventory Updates**: Handle approved transfer requests
4. **Donor Tracking**: Update last donation dates
5. **Daily Cleanup**: Remove expired blood units

---

## 📊 API Endpoints

### **Public Routes**
- `GET /` - Homepage with blood availability
- `GET /donate` - Donation appointment form
- `POST /donate` - Submit appointment request

### **Hospital Routes**
- `POST /hospital/login` - Hospital authentication
- `GET /hospital/dashboard` - Main dashboard
- `GET /hospital/inventory` - Blood inventory management
- `POST /hospital/add_blood` - Add blood units
- `GET /hospital/appointments` - Manage appointments
- `GET /hospital/network` - View network availability
- `POST /hospital/request_blood` - Request blood transfer

### **Admin Routes**
- `POST /admin/login` - Admin authentication
- `GET /admin/dashboard` - System overview
- `GET /admin/hospitals` - Hospital management
- `POST /admin/add_hospital` - Register new hospital
- `GET /admin/logs` - System activity logs

### **API Endpoints**
- `GET /api/hospitals/<city>` - Get hospitals by city
- `GET /api/blood_availability/<hospital_id>` - Blood stock info

---

## 🎓 Educational Value

### **Learning Outcomes**
- Multi-role web application architecture
- Database design with triggers and constraints
- Dark theme UI/UX implementation
- Real-time data management
- Emergency system protocols
- Audit trail implementation

### **Technologies Demonstrated**
- **Backend**: Python Flask, MySQL, bcrypt
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: MySQL triggers, events, constraints
- **Security**: Password hashing, session management
- **Design**: Dark theme, responsive layout

---

## 🚀 Production Readiness

### **Security Features**
- Password hashing with bcrypt
- SQL injection prevention
- Input validation and sanitization
- Session management
- Role-based access control

### **Performance Optimizations**
- Database indexing
- Connection pooling ready
- Efficient queries
- Minimal resource usage
- Scalable architecture

---

## 🧪 Testing Scenarios

### **Test Case 1: Complete Donor Flow**
1. Visit homepage → View blood availability
2. Book appointment → Select hospital
3. Hospital login → Approve appointment
4. Complete donation → Add blood to inventory

### **Test Case 2: Emergency Transfer**
1. Hospital A login → Check low inventory
2. View network → Find available blood
3. Request transfer → Set urgency level
4. Hospital B login → Approve request
5. Verify inventory updates

### **Test Case 3: Admin Management**
1. Admin login → View system stats
2. Register new hospital → Provide credentials
3. Monitor system logs → Track activities
4. Generate reports → System analytics

---

## 🎯 Key Achievements

### ✅ **Fully Implemented Features**
- [x] Multi-role authentication system
- [x] Dark theme responsive UI
- [x] Real-time blood inventory management
- [x] Hospital-to-hospital network
- [x] Emergency blood transfer protocols
- [x] Automated expiry management
- [x] Complete audit logging
- [x] 90-day donation rule enforcement
- [x] Mobile-responsive design
- [x] Form validation and security

### 🚫 **Admin Limitations (By Design)**
- ❌ Cannot approve blood transfers
- ❌ Cannot add blood inventory
- ❌ Cannot handle donor appointments
- ❌ Cannot manage emergency requests

*This ensures real-time hospital-to-hospital communication without administrative bottlenecks.*

---

## 📞 Support & Documentation

- **Setup Guide**: `SETUP_INSTRUCTIONS.md`
- **Database Design**: `ER_DIAGRAM.md`
- **Demo Credentials**: Included in login pages
- **API Documentation**: Available in code comments

---

## 🏆 System Status

**✅ Production Ready**
- Complete functionality implemented
- Dark theme UI fully responsive
- Database with automated triggers
- Multi-role architecture working
- Security measures in place
- Comprehensive documentation

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Ready for deployment

---

*Built with ❤️ for saving lives through technology*
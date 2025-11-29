-- Complete Blood Bank Database Schema
CREATE DATABASE IF NOT EXISTS blood_bank_db;
USE blood_bank_db;

-- Drop existing tables
DROP TABLE IF EXISTS transfer_requests;
DROP TABLE IF EXISTS donation_appointments;
DROP TABLE IF EXISTS hospital_inventory;
DROP TABLE IF EXISTS rare_donors;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS inventory_logs;
DROP TABLE IF EXISTS emergency_requests;
DROP TABLE IF EXISTS blood_inventory;
DROP TABLE IF EXISTS donors;
DROP TABLE IF EXISTS hospitals;

-- Hospitals Table
CREATE TABLE hospitals (
    hospital_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    city VARCHAR(100) NOT NULL,
    reliability_score DECIMAL(3,2) DEFAULT 3.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Donors Table
CREATE TABLE donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    phone VARCHAR(15),
    city VARCHAR(100),
    goodwill_score INT DEFAULT 0,
    last_donation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rare Donors Table
CREATE TABLE rare_donors (
    rare_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE CASCADE
);

-- Hospital Inventory Table
CREATE TABLE hospital_inventory (
    h_bag_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units_available INT NOT NULL DEFAULT 0,
    expires_on DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id) ON DELETE CASCADE
);

-- Donation Appointments Table
CREATE TABLE donation_appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT,
    hospital_id INT,
    preferred_time DATETIME NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected', 'Completed') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE CASCADE,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id) ON DELETE CASCADE
);

-- Transfer Requests Table
CREATE TABLE transfer_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    from_hospital INT,
    to_hospital INT,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units_needed INT NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_hospital) REFERENCES hospitals(hospital_id) ON DELETE CASCADE,
    FOREIGN KEY (to_hospital) REFERENCES hospitals(hospital_id) ON DELETE CASCADE
);

-- Emergency Requests Table
CREATE TABLE emergency_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT,
    requester_name VARCHAR(100) NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units_required INT NOT NULL,
    urgency ENUM('Low', 'Medium', 'High', 'Critical') DEFAULT 'Medium',
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    requested_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_on TIMESTAMP NULL,
    notes TEXT,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id) ON DELETE SET NULL
);

-- Blood Inventory Table (Legacy)
CREATE TABLE blood_inventory (
    bag_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    collected_on DATE NOT NULL,
    expires_on DATE NOT NULL,
    status ENUM('Available', 'Expired', 'Used') DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE SET NULL
);

-- Logs Table
CREATE TABLE logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory Logs Table
CREATE TABLE inventory_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    related_id INT,
    action_type ENUM('INSERT', 'EXPIRY', 'EMERGENCY_APPROVAL', 'STOCK_REDUCTION', 'LOGIN', 'LOGOUT') NOT NULL,
    details TEXT NOT NULL,
    user_type ENUM('Admin', 'Hospital') DEFAULT 'Admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Sample Data
INSERT INTO hospitals (name, email, password, address, phone, city) VALUES 
('MS Ramaiah Medical College', 'admin@msramaiah.com', '123456', 'MSRIT Post, MSR Nagar, Bangalore', '+91-80-2360-8888', 'Bangalore'),
('Manipal Hospital', 'admin@manipal.com', '123456', 'HAL Airport Road, Bangalore', '+91-80-2502-4444', 'Bangalore'),
('Apollo Hospital', 'admin@apollo.com', '123456', 'Bannerghatta Road, Bangalore', '+91-80-2630-0000', 'Bangalore'),
('Fortis Hospital', 'admin@fortis.com', '123456', 'Cunningham Road, Bangalore', '+91-80-6621-4444', 'Bangalore'),
('AIIMS Delhi', 'admin@aiims.com', '123456', 'Ansari Nagar, New Delhi', '+91-11-2658-8500', 'Delhi'),
('Kokilaben Hospital', 'admin@kokilaben.com', '123456', 'Four Bungalows, Mumbai', '+91-22-4269-8888', 'Mumbai'),
('Hinduja Hospital', 'admin@hinduja.com', '123456', 'Mahim, Mumbai', '+91-22-2445-2222', 'Mumbai'),
('Narayana Health', 'admin@narayana.com', '123456', 'Bommasandra, Bangalore', '+91-80-7122-2200', 'Bangalore'),
('Rainbow Children Hospital', 'admin@rainbow.com', '123456', 'Marathahalli, Bangalore', '+91-80-4092-2222', 'Bangalore');

INSERT INTO donors (name, age, gender, blood_group, phone, city, goodwill_score) VALUES
('Rajesh Kumar', 28, 'Male', 'O+', '9876543210', 'Bangalore', 5),
('Priya Sharma', 25, 'Female', 'A+', '9876543211', 'Bangalore', 3),
('Amit Singh', 32, 'Male', 'B+', '9876543212', 'Delhi', 7),
('Sneha Patel', 29, 'Female', 'AB+', '9876543213', 'Mumbai', 4),
('Vikram Reddy', 35, 'Male', 'O-', '9876543214', 'Bangalore', 8),
('Kavya Nair', 26, 'Female', 'A-', '9876543215', 'Bangalore', 6),
('Rohit Gupta', 31, 'Male', 'B-', '9876543216', 'Delhi', 5),
('Anita Joshi', 27, 'Female', 'AB-', '9876543217', 'Mumbai', 9);

INSERT INTO rare_donors (donor_id, reason) VALUES
(5, 'O- Universal donor'),
(6, 'A- Rare type'),
(7, 'B- Rare type'),
(8, 'AB- Rarest type');

INSERT INTO hospital_inventory (hospital_id, blood_group, units_available, expires_on) VALUES
(1, 'O+', 15, '2024-03-15'),
(1, 'A+', 8, '2024-03-20'),
(2, 'B+', 12, '2024-03-18'),
(3, 'AB+', 5, '2024-03-25'),
(4, 'O-', 3, '2024-03-22'),
(5, 'A-', 7, '2024-03-28');

INSERT INTO transfer_requests (from_hospital, to_hospital, blood_group, units_needed, status) VALUES
(1, 2, 'O+', 5, 'Pending'),
(3, 4, 'A+', 3, 'Approved');
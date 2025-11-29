-- Blood Bank & Emergency Availability Monitoring System
-- Database Schema

CREATE DATABASE IF NOT EXISTS blood_bank_db;
USE blood_bank_db;

-- 1. Hospitals Table (must be created first for foreign keys)
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

-- 2. Donors Table
CREATE TABLE donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    city VARCHAR(100) NOT NULL,
    last_donation_date DATE,
    goodwill_score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Hospital Inventory Table
CREATE TABLE hospital_inventory (
    h_bag_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units_available INT NOT NULL DEFAULT 0,
    expires_on DATE NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
);

-- 4. Transfer Requests Table
CREATE TABLE transfer_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    from_hospital INT,
    to_hospital INT,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units_needed INT NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_hospital) REFERENCES hospitals(hospital_id),
    FOREIGN KEY (to_hospital) REFERENCES hospitals(hospital_id)
);

-- 5. Donation Appointments Table
CREATE TABLE donation_appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT,
    hospital_id INT,
    preferred_time DATETIME NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id),
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
);

-- 6. Rare Donors Table
CREATE TABLE rare_donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT,
    reason VARCHAR(255) DEFAULT 'Rare blood type',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id)
);

-- 7. Logs Table
CREATE TABLE logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT,
    action_type ENUM('INVENTORY_ADD', 'INVENTORY_UPDATE', 'TRANSFER_REQUEST', 'TRANSFER_APPROVE', 'APPOINTMENT_APPROVE', 'EXPIRY') NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
);
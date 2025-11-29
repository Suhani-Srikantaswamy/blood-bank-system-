-- Blood Donation & Hospital Blood Network System Database Schema
-- Drop existing database if exists
DROP DATABASE IF EXISTS blood_network_db;
CREATE DATABASE blood_network_db;
USE blood_network_db;

-- Table: donors (Public donors - no login required)
CREATE TABLE donors (
    donor_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL CHECK (age >= 18 AND age <= 65),
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    phone VARCHAR(15) NOT NULL,
    city VARCHAR(50) NOT NULL,
    last_donation_date DATE DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_blood_group (blood_group),
    INDEX idx_city (city)
);

-- Table: hospitals (Hospital login accounts)
CREATE TABLE hospitals (
    hospital_id INT PRIMARY KEY AUTO_INCREMENT,
    hospital_name VARCHAR(100) NOT NULL UNIQUE,
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_city (city)
);

-- Table: donation_appointments (Donor appointment requests)
CREATE TABLE donation_appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    donor_id INT NOT NULL,
    hospital_id INT NOT NULL,
    preferred_time DATETIME NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected', 'Completed') DEFAULT 'Pending',
    notes TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE CASCADE,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_hospital (hospital_id)
);

-- Table: hospital_inventory (Each hospital's blood stock)
CREATE TABLE hospital_inventory (
    h_bag_id INT PRIMARY KEY AUTO_INCREMENT,
    hospital_id INT NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units_available INT NOT NULL DEFAULT 0 CHECK (units_available >= 0),
    expiry_date DATE NOT NULL,
    status ENUM('Available', 'Expired', 'Used', 'Transferred') DEFAULT 'Available',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id) ON DELETE CASCADE,
    INDEX idx_hospital_blood (hospital_id, blood_group),
    INDEX idx_expiry (expiry_date),
    INDEX idx_status (status)
);

-- Table: transfer_requests (Hospital-to-hospital blood requests)
CREATE TABLE transfer_requests (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    from_hospital_id INT NOT NULL,
    to_hospital_id INT NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units_needed INT NOT NULL CHECK (units_needed > 0),
    status ENUM('Pending', 'Approved', 'Denied') DEFAULT 'Pending',
    urgency ENUM('Low', 'Medium', 'High', 'Critical') DEFAULT 'Medium',
    notes TEXT DEFAULT NULL,
    requested_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_on TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (from_hospital_id) REFERENCES hospitals(hospital_id) ON DELETE CASCADE,
    FOREIGN KEY (to_hospital_id) REFERENCES hospitals(hospital_id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_to_hospital (to_hospital_id),
    INDEX idx_urgency (urgency)
);

-- Table: system_logs (System activity tracking)
CREATE TABLE system_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    action_type ENUM('DONATION_REQUEST', 'APPOINTMENT_APPROVED', 'BLOOD_ADDED', 'BLOOD_EXPIRED', 'TRANSFER_REQUEST', 'TRANSFER_APPROVED', 'BLOOD_USED', 'HOSPITAL_REGISTERED') NOT NULL,
    description TEXT NOT NULL,
    related_id INT DEFAULT NULL,
    hospital_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id) ON DELETE SET NULL,
    INDEX idx_action_type (action_type),
    INDEX idx_created_at (created_at)
);

-- Table: admins (Optional admin accounts - very limited role)
CREATE TABLE admins (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin account
INSERT INTO admins (username, password, email) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LQ4YCOuLQjKH5rTcswjFLBHc6T8FWO/BruB3S', 'admin@bloodnetwork.com');
-- Default password: admin123

-- Sample hospitals
INSERT INTO hospitals (hospital_name, address, city, email, password, phone) VALUES
('City General Hospital', '123 Main Street, Downtown', 'Mumbai', 'admin@citygeneral.com', '$2b$12$LQv3c1yqBWVHxkd0LQ4YCOuLQjKH5rTcswjFLBHc6T8FWO/BruB3S', '+91-9876543210'),
('Metro Medical Center', '456 Health Avenue, Central', 'Delhi', 'contact@metromedical.com', '$2b$12$LQv3c1yqBWVHxkd0LQ4YCOuLQjKH5rTcswjFLBHc6T8FWO/BruB3S', '+91-9876543211'),
('Regional Blood Bank', '789 Care Road, North Zone', 'Bangalore', 'info@regionalblood.com', '$2b$12$LQv3c1yqBWVHxkd0LQ4YCOuLQjKH5rTcswjFLBHc6T8FWO/BruB3S', '+91-9876543212');
-- Default password for all hospitals: hospital123

-- Sample inventory data
INSERT INTO hospital_inventory (hospital_id, blood_group, units_available, expiry_date) VALUES
(1, 'O+', 25, DATE_ADD(CURDATE(), INTERVAL 30 DAY)),
(1, 'A+', 15, DATE_ADD(CURDATE(), INTERVAL 25 DAY)),
(1, 'B+', 10, DATE_ADD(CURDATE(), INTERVAL 20 DAY)),
(2, 'O-', 8, DATE_ADD(CURDATE(), INTERVAL 35 DAY)),
(2, 'AB+', 12, DATE_ADD(CURDATE(), INTERVAL 28 DAY)),
(3, 'A-', 18, DATE_ADD(CURDATE(), INTERVAL 32 DAY)),
(3, 'B-', 6, DATE_ADD(CURDATE(), INTERVAL 22 DAY));
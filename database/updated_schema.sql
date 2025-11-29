-- Updated Blood Bank Management System Schema
-- Professional Version with Authentication

CREATE DATABASE IF NOT EXISTS blood_bank_db;
USE blood_bank_db;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS inventory_logs;
DROP TABLE IF EXISTS emergency_requests;
DROP TABLE IF EXISTS blood_inventory;
DROP TABLE IF EXISTS donors;
DROP TABLE IF EXISTS hospitals;

-- 1. Hospitals Table (for login system)
CREATE TABLE hospitals (
    hospital_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Donors Table
CREATE TABLE donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    phone VARCHAR(15),
    last_donation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Blood Inventory Table
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

-- 4. Emergency Requests Table (Updated)
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

-- 5. Inventory Logs Table
CREATE TABLE inventory_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    related_id INT,
    action_type ENUM('INSERT', 'EXPIRY', 'EMERGENCY_APPROVAL', 'STOCK_REDUCTION', 'LOGIN', 'LOGOUT') NOT NULL,
    details TEXT NOT NULL,
    user_type ENUM('Admin', 'Hospital') DEFAULT 'Admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin credentials (password: admin123)
INSERT INTO hospitals (hospital_name, email, password) VALUES 
('System Admin', 'admin@bloodbank.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj0kPjiYS.W2');

-- Insert sample hospitals
INSERT INTO hospitals (hospital_name, email, password) VALUES 
('City General Hospital', 'city@hospital.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj0kPjiYS.W2'),
('Metro Medical Center', 'metro@medical.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj0kPjiYS.W2');
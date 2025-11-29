-- Users and Authentication Tables

USE blood_bank_db;

-- Admin Users Table
CREATE TABLE admin_users (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hospital Users Table  
CREATE TABLE hospitals (
    hospital_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Demo Admin User
INSERT INTO admin_users (email, password, name) VALUES 
('admin@bloodbank.com', 'admin123', 'System Administrator');

-- Insert Demo Hospital Users
INSERT INTO hospitals (name, email, password, address, phone) VALUES 
('City General Hospital', 'admin@citygeneral.com', 'hospital123', '123 Main St, City', '555-0101'),
('Metro Medical Center', 'contact@metromedical.com', 'hospital123', '456 Oak Ave, Metro', '555-0102'),
('Regional Blood Center', 'info@regionalblood.com', 'hospital123', '789 Pine Rd, Regional', '555-0103');
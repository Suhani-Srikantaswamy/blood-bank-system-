-- BloodBank Pro Seed Data
-- Run this after schema.sql to populate with test data

USE blood_bank_db;

-- 1. INSERT 8 HOSPITALS (Skip if already exists)
INSERT IGNORE INTO hospitals (name, city, email, password, phone, reliability_score) VALUES
('Apollo Hospitals', 'Ahmedabad', 'apollo@gmail.com', '123456', '9876543210', 0),
('Manipal Hospital', 'Ranchi', 'manipal@gmail.com', '123456', '9876543211', 0),
('Fortis Hospital', 'Mysore', 'fortis@gmail.com', '123456', '9876543212', 0),
('AIIMS Hospital', 'Delhi', 'aiims@gmail.com', '123456', '9876543213', 0),
('Kokilaben Hospital', 'Jaipur', 'kokilaben@gmail.com', '123456', '9876543214', 0),
('Hinduja Hospital', 'Pune', 'hinduja@gmail.com', '123456', '9876543215', 0),
('Narayana Health', 'Kolkata', 'narayana@gmail.com', '123456', '9876543216', 0),
('Rainbow Hospital', 'Hyderabad', 'rainbow@gmail.com', '123456', '9876543217', 0);

-- 2. INSERT DONORS FOR EACH HOSPITAL

-- Apollo Hospital Donors (Ahmedabad)
INSERT INTO donors (name, age, gender, blood_group, phone, city, goodwill_score) VALUES
('Rohan Verma', 28, 'Male', 'A+', '8901234567', 'Ahmedabad', 0),
('Sneha Iyer', 25, 'Female', 'O+', '8901234568', 'Ahmedabad', 0),
('Karthik Rao', 32, 'Male', 'AB+', '8901234569', 'Ahmedabad', 0),
('Dia Shetty', 29, 'Female', 'B+', '8901234570', 'Ahmedabad', 0),
('Manish Kumar', 35, 'Male', 'O-', '8901234571', 'Gandhinagar', 0);

-- Manipal Hospital Donors (Ranchi)
INSERT INTO donors (name, age, gender, blood_group, phone, city, goodwill_score) VALUES
('Sujith Kumar', 30, 'Male', 'A+', '8901234572', 'Ranchi', 0),
('Aisha Khan', 27, 'Female', 'O-', '8901234573', 'Ranchi', 0),
('Rahul Gopal', 33, 'Male', 'B-', '8901234574', 'Ranchi', 0),
('Nidhi Sharma', 26, 'Female', 'AB-', '8901234575', 'Jamshedpur', 0);

-- Fortis Hospital Donors (Mysore)
INSERT INTO donors (name, age, gender, blood_group, phone, city, goodwill_score) VALUES
('Aman Chopra', 31, 'Male', 'O+', '8901234576', 'Mysore', 0),
('Pooja Singh', 24, 'Female', 'AB+', '8901234577', 'Mysore', 0),
('Kunal Mehta', 29, 'Male', 'A-', '8901234578', 'Bangalore', 0);

-- AIIMS Hospital Donors (Delhi)
INSERT INTO donors (name, age, gender, blood_group, phone, city, goodwill_score) VALUES
('Tania Roy', 28, 'Female', 'B+', '8901234579', 'Delhi', 0),
('Arjun Malhotra', 34, 'Male', 'A+', '8901234580', 'Delhi', 0),
('Deepak Kumar', 30, 'Male', 'O-', '8901234581', 'Gurgaon', 0);

-- Kokilaben Hospital Donors (Jaipur)
INSERT INTO donors (name, age, gender, blood_group, phone, city, goodwill_score) VALUES
('Ritika Doshi', 26, 'Female', 'A-', '8901234582', 'Jaipur', 0),
('Sameer Patil', 32, 'Male', 'O+', '8901234583', 'Jaipur', 0),
('Meera Joshi', 27, 'Female', 'AB-', '8901234584', 'Udaipur', 0);

-- Hinduja Hospital Donors (Pune)
INSERT INTO donors (name, age, gender, blood_group, phone, city, goodwill_score) VALUES
('Sagar Thakur', 29, 'Male', 'B+', '8901234585', 'Pune', 0),
('Ananya Shah', 25, 'Female', 'O+', '8901234586', 'Pune', 0),
('Pratik Naik', 33, 'Male', 'A+', '8901234587', 'Mumbai', 0);

-- Narayana Health Donors (Kolkata)
INSERT INTO donors (name, age, gender, blood_group, phone, city, goodwill_score) VALUES
('Rituparna Sen', 28, 'Female', 'O-', '8901234588', 'Kolkata', 0),
('Abir Roy', 31, 'Male', 'B-', '8901234589', 'Kolkata', 0),
('Rishika Bose', 26, 'Female', 'AB+', '8901234590', 'Howrah', 0);

-- Rainbow Hospital Donors (Hyderabad)
INSERT INTO donors (name, age, gender, blood_group, phone, city, goodwill_score) VALUES
('Shiva Reddy', 30, 'Male', 'O+', '8901234591', 'Hyderabad', 0),
('Kavya Reddy', 27, 'Female', 'A-', '8901234592', 'Hyderabad', 0),
('Varun Tej', 32, 'Male', 'B-', '8901234593', 'Hyderabad', 0),
('Shalini Devi', 24, 'Female', 'AB+', '8901234594', 'Secunderabad', 0);

-- 3. INSERT TRANSFER REQUESTS (Including Ramaiah)
-- Note: Get hospital IDs first, then insert transfers

INSERT INTO transfer_requests (from_hospital, to_hospital, blood_group, units_needed, status, created_at) VALUES
-- Apollo (1) → Manipal (2)
(1, 2, 'A+', 3, 'Approved', '2024-01-15 10:30:00'),
-- AIIMS (4) → Kokilaben (5)
(4, 5, 'A-', 2, 'Pending', '2024-01-16 14:20:00'),
-- Hinduja (6) → Narayana (7)
(6, 7, 'B+', 1, 'Completed', '2024-01-17 09:15:00'),
-- Fortis (3) → Rainbow (8)
(3, 8, 'B-', 2, 'Approved', '2024-01-18 11:45:00'),
-- Manipal (2) → AIIMS (4)
(2, 4, 'O+', 5, 'Pending', '2024-01-19 16:30:00'),
-- Narayana (7) → Apollo (1)
(7, 1, 'O-', 1, 'Rejected', '2024-01-20 08:20:00'),
-- Kokilaben (5) → Fortis (3)
(5, 3, 'AB+', 2, 'Completed', '2024-01-21 13:10:00'),
-- Rainbow (8) → Hinduja (6)
(8, 6, 'AB-', 1, 'Approved', '2024-01-22 15:40:00'),
-- Ramaiah transfers (assuming Ramaiah has hospital_id based on existing data)
-- Ramaiah → Apollo
((SELECT hospital_id FROM hospitals WHERE name LIKE '%Ramaiah%' LIMIT 1), 1, 'O+', 2, 'Pending', '2024-01-23 10:00:00'),
-- Manipal → Ramaiah
(2, (SELECT hospital_id FROM hospitals WHERE name LIKE '%Ramaiah%' LIMIT 1), 'A+', 3, 'Approved', '2024-01-24 12:30:00'),
-- AIIMS → Ramaiah
(4, (SELECT hospital_id FROM hospitals WHERE name LIKE '%Ramaiah%' LIMIT 1), 'B-', 1, 'Completed', '2024-01-25 14:15:00');

-- 4. INSERT SAMPLE HOSPITAL INVENTORY
INSERT INTO hospital_inventory (hospital_id, blood_group, units_available, expires_on) VALUES
-- Apollo Hospital inventory
(1, 'A+', 15, '2024-03-15'),
(1, 'O+', 12, '2024-03-20'),
(1, 'B+', 8, '2024-03-10'),
(1, 'AB+', 5, '2024-03-25'),
-- Manipal Hospital inventory
(2, 'A+', 10, '2024-03-18'),
(2, 'O-', 6, '2024-03-12'),
(2, 'B-', 4, '2024-03-22'),
(2, 'AB-', 3, '2024-03-28'),
-- Fortis Hospital inventory
(3, 'O+', 18, '2024-03-16'),
(3, 'A-', 7, '2024-03-14'),
(3, 'B+', 9, '2024-03-21'),
-- AIIMS Hospital inventory
(4, 'A+', 20, '2024-03-17'),
(4, 'O+', 25, '2024-03-19'),
(4, 'AB+', 8, '2024-03-23'),
(4, 'O-', 12, '2024-03-26'),
-- Kokilaben Hospital inventory
(5, 'B+', 14, '2024-03-13'),
(5, 'A-', 6, '2024-03-24'),
(5, 'AB-', 4, '2024-03-27'),
-- Hinduja Hospital inventory
(6, 'O+', 16, '2024-03-11'),
(6, 'A+', 11, '2024-03-29'),
(6, 'B-', 5, '2024-03-30'),
-- Narayana Health inventory
(7, 'AB+', 9, '2024-03-31'),
(7, 'O-', 7, '2024-04-01'),
(7, 'A-', 8, '2024-04-02'),
-- Rainbow Hospital inventory
(8, 'B+', 13, '2024-04-03'),
(8, 'O+', 19, '2024-04-04'),
(8, 'AB-', 6, '2024-04-05');

-- 5. INSERT SAMPLE DONATION APPOINTMENTS
INSERT INTO donation_appointments (donor_id, hospital_id, preferred_time, status) VALUES
-- Recent appointments
(1, 1, '2024-02-01 10:00:00', 'Approved'),
(2, 1, '2024-02-02 11:30:00', 'Completed'),
(6, 2, '2024-02-03 09:15:00', 'Pending'),
(7, 2, '2024-02-04 14:20:00', 'Approved'),
(10, 3, '2024-02-05 16:45:00', 'Pending'),
(13, 4, '2024-02-06 08:30:00', 'Completed'),
(16, 5, '2024-02-07 13:10:00', 'Approved'),
(19, 6, '2024-02-08 15:25:00', 'Pending'),
(22, 7, '2024-02-09 10:40:00', 'Approved'),
(25, 8, '2024-02-10 12:15:00', 'Pending');

-- 6. INSERT RARE DONORS (for special blood types)
INSERT INTO rare_donors (donor_id, reason) VALUES
(5, 'O- Universal Donor'),
(7, 'O- Universal Donor'),
(8, 'B- Rare Type'),
(9, 'AB- Rare Type'),
(12, 'A- Rare Type'),
(15, 'AB- Rare Type'),
(17, 'B- Rare Type'),
(21, 'O- Universal Donor'),
(23, 'B- Rare Type'),
(27, 'B- Rare Type');

-- 7. INSERT SYSTEM LOGS
INSERT INTO inventory_logs (related_id, action_type, details) VALUES
(1, 'INSERT', 'New blood bag added - A+ from Apollo Hospital'),
(2, 'INSERT', 'New blood bag added - O+ from Manipal Hospital'),
(3, 'EMERGENCY_APPROVAL', 'Emergency request approved for B+ blood'),
(4, 'INSERT', 'New blood bag added - AB- from AIIMS Hospital'),
(5, 'EXPIRY', 'Blood bag expired - A+ from Kokilaben Hospital');

-- Display confirmation
SELECT 'Seed data inserted successfully!' as Status;
SELECT COUNT(*) as 'Total Hospitals' FROM hospitals;
SELECT COUNT(*) as 'Total Donors' FROM donors;
SELECT COUNT(*) as 'Total Transfer Requests' FROM transfer_requests;
SELECT COUNT(*) as 'Total Inventory Items' FROM hospital_inventory;
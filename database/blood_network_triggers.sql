-- Blood Network System MySQL Triggers
USE blood_network_db;

-- Trigger 1: Auto-expire blood units past expiry date
DELIMITER $$
CREATE TRIGGER auto_expire_blood
BEFORE UPDATE ON hospital_inventory
FOR EACH ROW
BEGIN
    IF NEW.expiry_date < CURDATE() AND OLD.status = 'Available' THEN
        SET NEW.status = 'Expired';
        INSERT INTO system_logs (action_type, description, related_id, hospital_id)
        VALUES ('BLOOD_EXPIRED', 
                CONCAT('Blood unit expired: ', NEW.blood_group, ' (', NEW.units_available, ' units) at hospital ID ', NEW.hospital_id),
                NEW.h_bag_id, NEW.hospital_id);
    END IF;
END$$
DELIMITER ;

-- Trigger 2: Auto-log new blood entries
DELIMITER $$
CREATE TRIGGER log_new_blood_entry
AFTER INSERT ON hospital_inventory
FOR EACH ROW
BEGIN
    INSERT INTO system_logs (action_type, description, related_id, hospital_id)
    VALUES ('BLOOD_ADDED', 
            CONCAT('New blood added: ', NEW.blood_group, ' (', NEW.units_available, ' units) - Expires: ', NEW.expiry_date),
            NEW.h_bag_id, NEW.hospital_id);
END$$
DELIMITER ;

-- Trigger 3: Auto-decrease inventory on transfer approval
DELIMITER $$
CREATE TRIGGER handle_transfer_approval
AFTER UPDATE ON transfer_requests
FOR EACH ROW
BEGIN
    IF NEW.status = 'Approved' AND OLD.status = 'Pending' THEN
        -- Decrease inventory from source hospital
        UPDATE hospital_inventory 
        SET units_available = units_available - NEW.units_needed,
            status = CASE 
                WHEN units_available - NEW.units_needed <= 0 THEN 'Transferred'
                ELSE 'Available'
            END
        WHERE hospital_id = NEW.from_hospital_id 
        AND blood_group = NEW.blood_group 
        AND status = 'Available'
        AND units_available >= NEW.units_needed
        LIMIT 1;
        
        -- Add inventory to destination hospital
        INSERT INTO hospital_inventory (hospital_id, blood_group, units_available, expiry_date)
        VALUES (NEW.to_hospital_id, NEW.blood_group, NEW.units_needed, DATE_ADD(CURDATE(), INTERVAL 35 DAY))
        ON DUPLICATE KEY UPDATE 
        units_available = units_available + NEW.units_needed;
        
        -- Log the transfer
        INSERT INTO system_logs (action_type, description, related_id, hospital_id)
        VALUES ('TRANSFER_APPROVED', 
                CONCAT('Blood transfer approved: ', NEW.units_needed, ' units of ', NEW.blood_group, 
                       ' from hospital ', NEW.from_hospital_id, ' to hospital ', NEW.to_hospital_id),
                NEW.request_id, NEW.from_hospital_id);
        
        -- Update resolved timestamp
        UPDATE transfer_requests 
        SET resolved_on = CURRENT_TIMESTAMP 
        WHERE request_id = NEW.request_id;
    END IF;
END$$
DELIMITER ;

-- Trigger 4: Auto-update last donation date when appointment completed
DELIMITER $$
CREATE TRIGGER update_donor_last_donation
AFTER UPDATE ON donation_appointments
FOR EACH ROW
BEGIN
    IF NEW.status = 'Completed' AND OLD.status != 'Completed' THEN
        UPDATE donors 
        SET last_donation_date = CURDATE()
        WHERE donor_id = NEW.donor_id;
        
        INSERT INTO system_logs (action_type, description, related_id, hospital_id)
        VALUES ('APPOINTMENT_APPROVED', 
                CONCAT('Donation completed by donor ID ', NEW.donor_id, ' at hospital ID ', NEW.hospital_id),
                NEW.appointment_id, NEW.hospital_id);
    END IF;
END$$
DELIMITER ;

-- Trigger 5: Log donation appointment requests
DELIMITER $$
CREATE TRIGGER log_donation_request
AFTER INSERT ON donation_appointments
FOR EACH ROW
BEGIN
    INSERT INTO system_logs (action_type, description, related_id, hospital_id)
    VALUES ('DONATION_REQUEST', 
            CONCAT('New donation appointment requested by donor ID ', NEW.donor_id, ' for ', NEW.preferred_time),
            NEW.appointment_id, NEW.hospital_id);
END$$
DELIMITER ;

-- Trigger 6: Log transfer requests
DELIMITER $$
CREATE TRIGGER log_transfer_request
AFTER INSERT ON transfer_requests
FOR EACH ROW
BEGIN
    INSERT INTO system_logs (action_type, description, related_id, hospital_id)
    VALUES ('TRANSFER_REQUEST', 
            CONCAT('Blood transfer requested: ', NEW.units_needed, ' units of ', NEW.blood_group, 
                   ' from hospital ', NEW.from_hospital_id, ' to hospital ', NEW.to_hospital_id),
            NEW.request_id, NEW.from_hospital_id);
END$$
DELIMITER ;

-- Trigger 7: Log hospital registrations
DELIMITER $$
CREATE TRIGGER log_hospital_registration
AFTER INSERT ON hospitals
FOR EACH ROW
BEGIN
    INSERT INTO system_logs (action_type, description, related_id, hospital_id)
    VALUES ('HOSPITAL_REGISTERED', 
            CONCAT('New hospital registered: ', NEW.hospital_name, ' in ', NEW.city),
            NEW.hospital_id, NEW.hospital_id);
END$$
DELIMITER ;

-- Event to automatically expire blood units daily
DELIMITER $$
CREATE EVENT daily_blood_expiry_check
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    UPDATE hospital_inventory 
    SET status = 'Expired' 
    WHERE expiry_date < CURDATE() AND status = 'Available';
END$$
DELIMITER ;

-- Enable event scheduler
SET GLOBAL event_scheduler = ON;
-- Database Triggers for Blood Bank System

USE blood_bank_db;

-- Trigger 1: Auto-expire inventory units
DELIMITER $$
CREATE TRIGGER auto_expire_inventory
BEFORE UPDATE ON hospital_inventory
FOR EACH ROW
BEGIN
    IF NEW.expires_on < CURDATE() AND OLD.units_available > 0 THEN
        SET NEW.units_available = 0;
        INSERT INTO logs (hospital_id, action_type, description) 
        VALUES (NEW.hospital_id, 'EXPIRY', CONCAT('Auto-expired ', OLD.units_available, ' units of ', NEW.blood_group));
    END IF;
END$$

-- Trigger 2: Log inventory additions
CREATE TRIGGER log_inventory_add
AFTER INSERT ON hospital_inventory
FOR EACH ROW
BEGIN
    INSERT INTO logs (hospital_id, action_type, description) 
    VALUES (NEW.hospital_id, 'INVENTORY_ADD', CONCAT('Added ', NEW.units_available, ' units of ', NEW.blood_group));
END$$

-- Trigger 3: Update goodwill score after donation completion
CREATE TRIGGER update_goodwill_score
AFTER UPDATE ON donation_appointments
FOR EACH ROW
BEGIN
    IF NEW.status = 'Completed' AND OLD.status != 'Completed' THEN
        UPDATE donors 
        SET goodwill_score = goodwill_score + 10,
            last_donation_date = CURDATE()
        WHERE donor_id = NEW.donor_id;
    END IF;
END$$

-- Trigger 4: Auto-decrease inventory after transfer approval
CREATE TRIGGER auto_transfer_inventory
AFTER UPDATE ON transfer_requests
FOR EACH ROW
BEGIN
    IF NEW.status = 'Approved' AND OLD.status = 'Pending' THEN
        -- Decrease from source hospital
        UPDATE hospital_inventory 
        SET units_available = units_available - NEW.units_needed
        WHERE hospital_id = NEW.from_hospital 
        AND blood_group = NEW.blood_group 
        AND units_available >= NEW.units_needed;
        
        -- Increase at destination hospital
        INSERT INTO hospital_inventory (hospital_id, blood_group, units_available, expires_on)
        VALUES (NEW.to_hospital, NEW.blood_group, NEW.units_needed, DATE_ADD(CURDATE(), INTERVAL 90 DAY))
        ON DUPLICATE KEY UPDATE units_available = units_available + NEW.units_needed;
        
        -- Log the transfer
        INSERT INTO logs (hospital_id, action_type, description) 
        VALUES (NEW.from_hospital, 'TRANSFER_APPROVE', 
                CONCAT('Transferred ', NEW.units_needed, ' units of ', NEW.blood_group, ' to hospital ID ', NEW.to_hospital));
    END IF;
END$$

DELIMITER ;
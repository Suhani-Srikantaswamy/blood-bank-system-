-- Fixed SQL Triggers for Blood Bank System

USE blood_bank_db;

-- 1. New Blood Bag Trigger
DELIMITER $$
CREATE TRIGGER new_blood_bag_log
AFTER INSERT ON blood_inventory
FOR EACH ROW
BEGIN
    INSERT INTO inventory_logs (related_id, action_type, details)
    VALUES (NEW.bag_id, 'INSERT', CONCAT('New blood bag added - Blood Group: ', NEW.blood_group, ', Donor ID: ', NEW.donor_id));
END$$
DELIMITER ;

-- 2. Emergency Request Approval Trigger
DELIMITER $$
CREATE TRIGGER emergency_approval_trigger
AFTER UPDATE ON emergency_requests
FOR EACH ROW
BEGIN
    DECLARE units_to_deduct INT;
    DECLARE bags_updated INT DEFAULT 0;
    
    IF NEW.status = 'Approved' AND OLD.status = 'Pending' THEN
        SET units_to_deduct = NEW.units_required;
        
        UPDATE blood_inventory 
        SET status = 'Used' 
        WHERE blood_group = NEW.blood_group 
        AND status = 'Available' 
        AND expires_on >= CURDATE()
        ORDER BY expires_on ASC
        LIMIT units_to_deduct;
        
        SET bags_updated = ROW_COUNT();
        
        INSERT INTO inventory_logs (related_id, action_type, details)
        VALUES (NEW.request_id, 'EMERGENCY_APPROVAL', 
                CONCAT('Emergency request approved - ', bags_updated, ' units of ', NEW.blood_group, ' deducted'));
        
        UPDATE emergency_requests 
        SET approved_on = NOW() 
        WHERE request_id = NEW.request_id;
    END IF;
END$$
DELIMITER ;

-- 3. Donor Last Donation Update Trigger
DELIMITER $$
CREATE TRIGGER update_donor_last_donation
AFTER INSERT ON blood_inventory
FOR EACH ROW
BEGIN
    UPDATE donors 
    SET last_donation_date = NEW.collected_on 
    WHERE donor_id = NEW.donor_id;
END$$
DELIMITER ;
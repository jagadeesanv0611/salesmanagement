# step - 1 create database:
CREATE DATABASE Sales_Intelligence_Hub;

# step - 2  use database:
USE Sales_Intelligence_Hub;

# step - 3 create branches table:
CREATE TABLE branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    branch_admin_name VARCHAR(100) NOT NULL
);

# step - 4 create customer
CREATE TABLE customer_sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT,
    date DATE NOT NULL,
    name VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(15),
    product_name VARCHAR(50),
    gross_sales DECIMAL(12,2) NOT NULL,
    received_amount DECIMAL(12,2) DEFAULT 0.00,
    pending_amount DECIMAL(12,2) GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status ENUM('open','close'),
    foreign key (branch_id) references branches(branch_id)
);

# step - 5 to create users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    branch_id INT,
    role ENUM('Super admin', 'Admin') NOT NULL,
    email VARCHAR(255) UNIQUE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

# step - 6 to create payment splits table
CREATE TABLE payment_splits (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT,
    payment_date DATE NOT NULL,
    amount_paid DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50),
    FOREIGN KEY (sale_id) REFERENCES customer_sales(sale_id)
);

#step - 7 to create trigger for payment splits:
#step - 7.1 need to create trigger after payment insert:  
#       A delimiter in SQL is a symbol (like ;, $$, or //) that tells the database where one SQL statement ends and the next begins.
DELIMITER $$
CREATE TRIGGER after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW

#step - 7.2 need to begin the statement:
BEGIN
    #step 7.2.1 need to declare a variable:
    DECLARE total_received DECIMAL(12,2);
    
    #step 7.2.2 need to sum all payments of the all sale:
    SELECT SUM(amount_paid) INTO total_received FROM payment_splits WHERE sale_id = NEW.sale_id;

    #step 7.2.3 need to update main sale record:
    UPDATE customer_sales SET received_amount = total_received WHERE sale_id = NEW.sale_id;
# step - 7.3 - to End and reset the statement: ends the trigger block
END$$     
# step - 7.4 - restores default Sql statement delimeter:
DELIMITER ;
commit;

INSERT INTO branches (branch_name, branch_admin_name) VALUES
('Branch_A', 'Priya'),
('Branch_B', 'Rajesh'),
('Branch_C', 'pavi'),
('Branch_D', 'Ganesh'),
('Branch_E', 'Chitra');

INSERT INTO users (username, user_password, branch_id, role, email) VALUES
('superadmin_1', 'pass@s123', NULL, 'Super admin', 'superadmin_1@gmail.com'),
('admin_a', 'pass@a123', 1, 'Admin', 'admin_a@gmail.com'),
('admin_b', 'pass@b123', 2, 'Admin', 'admin_b@gmail.com'),
('admin_c', 'pass@c123', 3, 'Admin', 'admin_c@gmail.com'),
('admin_d', 'pass@d123', 4, 'Admin', 'admin_d@gmail.com'),
('admin_e', 'pass@e123', 5, 'Admin', 'admin_e@gmail.com');

INSERT INTO customer_sales (branch_id, date, name, mobile_number, product_name, gross_sales, status) VALUES
(1, '2026-03-01', 'Vijay', '9876543210', 'Product A', 50000.00, 'open'),
(2, '2026-03-02', 'Surya', '9876543211', 'Product B', 30000.00, 'open'),
(3, '2026-03-03', 'Trisha', '9876543212', 'Product C', 70000.00, 'open'),
(4, '2026-03-04', 'Ajith', '9876543213', 'Product D', 45000.00, 'open'),
(5, '2026-03-05', 'Thara', '9876543214', 'Product E', 60000.00, 'open');

INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method) VALUES
(1, '2026-03-06', 20000.00, 'Cash'),
(2, '2026-03-06', 10000.00, 'Card'),
(3, '2026-03-07', 10000.00, 'UPI'),
(4, '2026-03-07', 15000.00, 'Cash'),
(5, '2026-03-08', 25000.00, 'Card');

#creating local host
CREATE USER 'apply_user'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON sales_intelligence_hub.* TO 'apply_user'@'localhost';
FLUSH PRIVILEGES;


# 1.Retrieve all records from the customer_sales table.
select * from customer_sales;

# 2.Retrieve all records from the branches table.
select * from branches;

# 3.Retrieve all records from the payment_splits table
select * from payment_splits;

# 4.Display all sales with status = 'Open'.
select * from customer_sales where status = 'open';

# 5.Retrieve all sales belonging to the B branch.
select * from customer_sales cs join branches b on cs.branch_id = b.branch_id 
where b.branch_name = 'Branch_B';

# 6.Calculate the total gross sales across all branches.
select sum(gross_sales) AS total_gross_sales from customer_sales;

# 7.Calculate the total received amount across all sales.
select sum(received_amount) as total_received_amount from customer_sales;

# 8.Calculate the total pending amount across all sales.
select sum(pending_amount) AS total_pending_amount from customer_sales;

# 9.Count the total number of sales per branch.
select count(cs.sale_id) as total_no_of_sales, b.branch_name from customer_sales cs 
join branches b on cs.branch_id = b.branch_id group by b.branch_name;

# 10.Find the average gross sales amount.
select cast(avg(gross_sales) as decimal(12,2)) AS average_gross_sales from customer_sales;
					#(or)
SELECT ROUND(AVG(gross_sales), 2) AS average_gross_sales FROM customer_sales;


# 11.Retrieve sales details along with the branch name.
select cs.*, b.branch_name from customer_sales cs join branches b on cs.branch_id = b.branch_id;

# 12.Retrieve sales details along with total payment received (using payment_splits).
select cs.*, sum(ps.amount_paid) as total_payment_received from customer_sales cs 
join payment_splits ps on cs.sale_id = ps.sale_id group by ps.sale_id;

# 13.Show branch-wise total gross sales (using JOIN & GROUP BY).
select sum(cs.gross_sales) as total_gross_sales, b.branch_name from customer_sales cs 
join branches b on cs.branch_id = b.branch_id group by b.branch_name;

# 14.Display sales along with payment method used.
select cs.*, ps.payment_method from customer_sales cs join payment_splits ps on cs.sale_id = ps.sale_id;

# 15.Retrieve sales along with branch admin name
select cs.*, b.branch_admin_name from customer_sales cs join branches b on cs.branch_id = b.branch_id;

# 16.Find sales where the pending amount is greater than 5000.
select * from customer_sales where pending_amount > '5000.00';

# 17.Retrieve top 3 highest gross sales
select * from customer_sales where status = 'open' order by gross_sales desc limit 3 ;

# 18.Find the branch with highest total gross sales
select sum(cs.gross_sales) as total_gross, b.branch_name from customer_sales cs 
join branches b on cs.branch_id = b.branch_id group by b.branch_name order by total_gross desc limit 1;

# 19.Retrieve monthly sales summary (group by month & year).
select year(date) as year, MONTH(date) as month, sum(gross_sales) as total_sales from customer_sales group by month(date), year(date) order by month, year;

#20.	Calculate payment method-wise total collection (Cash / UPI / Card).
select sum(amount_paid), payment_method from payment_splits group by payment_method;


DELETE FROM payment_splits WHERE sale_id IN (6,7,8);
DELETE FROM customer_sales WHERE sale_id IN (6,7,8);

DELETE FROM payment_splits WHERE sale_id IN (9,10,11);
DELETE FROM customer_sales WHERE sale_id IN (9,10,11);

SHOW INDEX FROM customer_sales;
ALTER TABLE customer_sales DROP INDEX mobile_number;
         
update customer_sales set received_amount = '5000.00' where date in ('2026-03-28');
update customer_sales set received_amount = '6000.00' where date = '2026-03-28';


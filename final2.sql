-- ===============================
-- Restaurant Management System (Normalized)
-- ===============================
drop database RestaurantDB1;
CREATE DATABASE IF NOT EXISTS RestaurantDB1;
USE RestaurantDB1;

-- ========== User Authentication ==========
CREATE TABLE IF NOT EXISTS UserLogin (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(100)
);

-- ========== Menu (created early to avoid FK errors) ==========
CREATE TABLE Menu (
    Menu_ID INT PRIMARY KEY
    -- Restaurant_ID FK will be added later via ALTER TABLE
);

-- ========== Customer and History ==========
CREATE TABLE Customer (
    Customer_ID INT PRIMARY KEY,
    Customer_FirstName VARCHAR(100),
    Customer_LastName VARCHAR(100),
    Email VARCHAR(100),
    Street VARCHAR(100),
    House_Number VARCHAR(10),
    City VARCHAR(50),
    Customer_type ENUM('P', 'R'),
    Customer_phone VARCHAR(20)
);

CREATE TABLE Customer_Phone (
    Customer_ID INT,
    Phone_Number VARCHAR(20),
    PRIMARY KEY (Customer_ID, Phone_Number),
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
);

CREATE TABLE Regular_Customer (
    R_Customer_ID INT PRIMARY KEY,
    FOREIGN KEY (R_Customer_ID) REFERENCES Customer(Customer_ID)
);

CREATE TABLE Premium_Customer (
    P_Customer_ID INT PRIMARY KEY,
    Discount_Rate DECIMAL(5,2),
    FOREIGN KEY (P_Customer_ID) REFERENCES Customer(Customer_ID)
);

CREATE TABLE Customer_History (
    History_ID INT PRIMARY KEY,
    Customer_ID INT,
    Order_ID INT,
    Date_Visited DATETIME,
    Feedback VARCHAR(255),
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
);

-- ========== Employee and Specializations ==========
CREATE TABLE Employee (
    Employee_ID INT PRIMARY KEY,
    Employee_FirstName VARCHAR(100),
    Employee_LastName VARCHAR(100),
    Salary DECIMAL(10,2),
    Phone VARCHAR(20),
    Role ENUM('D', 'W', 'C'),
    Username VARCHAR(50) UNIQUE,
    PasswordHash VARCHAR(255),
    Email VARCHAR(100)
);

CREATE TABLE Employee_Phone (
    Employee_ID INT,
    Phone VARCHAR(20),
    PRIMARY KEY (Employee_ID, Phone),
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Employee_ID)
);

CREATE TABLE Delivery_Boy (
    Employee_ID INT PRIMARY KEY,
    Availability BOOLEAN,
    Order_ID INT,
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Employee_ID)
);

CREATE TABLE Waiter (
    Employee_ID INT PRIMARY KEY,
    Table_assigned INT,
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Employee_ID)
);

CREATE TABLE Chef (
    Employee_ID INT PRIMARY KEY,
    Specialty VARCHAR(100),
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Employee_ID)
);

-- ========== Restaurant and geo_Location ==========
CREATE TABLE Restaurant (
    Restaurant_ID INT PRIMARY KEY,
    Email VARCHAR(100),
    Phone VARCHAR(20),
    Street VARCHAR(100),
    City VARCHAR(50),
    Opening_Hours TIME,
    Closing_Hours TIME,
    Menu_ID INT UNIQUE,
    geo_location_ID INT,
    FOREIGN KEY (Menu_ID) REFERENCES Menu(Menu_ID)
);

CREATE TABLE Restaurant_Phone (
    Restaurant_ID INT,
    Phone VARCHAR(20),
    PRIMARY KEY (Restaurant_ID, Phone),
    FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID)
);

CREATE TABLE geo_Location (
    geo_Location_ID INT,
    Restaurant_ID INT NOT NULL,
    Latitude FLOAT,
    Longitude FLOAT,
    PRIMARY KEY (geo_Location_ID, Restaurant_ID),
    FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID) ON DELETE CASCADE
);

-- ========== Delivery Area ==========
CREATE TABLE Delivery_Area (
    Area_code VARCHAR(20) PRIMARY KEY,
    City VARCHAR(50),
    Street VARCHAR(100)
);

-- ✅ New Junction Table: Many-to-Many between Delivery_Boy and Delivery_Area
CREATE TABLE Delivery_Assignment (
    Employee_ID INT,
    Area_Code VARCHAR(10),
    PRIMARY KEY (Employee_ID, Area_Code),
    FOREIGN KEY (Employee_ID) REFERENCES Delivery_Boy(Employee_ID) ON DELETE CASCADE,
    FOREIGN KEY (Area_Code) REFERENCES Delivery_Area(Area_code) ON DELETE CASCADE
);

CREATE TABLE Covered_by (
    geo_Location_ID INT,
    Restaurant_ID INT,
    Area_Code VARCHAR(20),
    PRIMARY KEY (geo_Location_ID, Restaurant_ID, Area_Code),
    FOREIGN KEY (geo_Location_ID, Restaurant_ID) REFERENCES geo_Location(geo_Location_ID, Restaurant_ID),
    FOREIGN KEY (Area_Code) REFERENCES Delivery_Area(Area_code)
);

-- ========== Add Restaurant_ID to Menu ==========
ALTER TABLE Menu
ADD Restaurant_ID INT UNIQUE,
ADD CONSTRAINT fk_menu_restaurant FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID);

-- ========== Menu Items ==========
CREATE TABLE Menu_Item (
    Item_ID INT PRIMARY KEY,
    Menu_ID INT,
    Name VARCHAR(100),
    Description VARCHAR(255),
    Category VARCHAR(50),
    Price DECIMAL(10,2),
    Is_Available BOOLEAN,
    FOREIGN KEY (Menu_ID) REFERENCES Menu(Menu_ID)
);

-- ========== Order and Related Tables ==========
CREATE TABLE Orders (
    Order_ID INT PRIMARY KEY,
    Order_Time DATETIME,
    Status VARCHAR(50),
    Customer_ID INT,
    Restaurant_ID INT,
    Order_Type ENUM('InDine', 'Delivery') NOT NULL,
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID),
    FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID)
);

CREATE TABLE contains (
    Order_ID INT,
    Item_ID INT,
    Quantity INT NOT NULL DEFAULT 1,
    PRIMARY KEY (Order_ID, Item_ID),
    FOREIGN KEY (Order_ID) REFERENCES Orders(Order_ID) on delete cascade,
    FOREIGN KEY (Item_ID) REFERENCES Menu_Item(Item_ID) on delete cascade
);

CREATE TABLE InDine_Order (
    Order_ID INT PRIMARY KEY,
    Table_number INT,
    FOREIGN KEY (Order_ID) REFERENCES Orders(Order_ID)
);

-- ========== Payment ==========
CREATE TABLE Payment (
    Payment_ID INT PRIMARY KEY,
    Total_payment DECIMAL(10,2),
    Order_ID INT NOT NULL,
    Payment_method ENUM('OL', 'CC', 'Ca'),
    Payment_Date date,
    FOREIGN KEY (Order_ID) REFERENCES Orders(Order_ID) on delete cascade
);

CREATE TABLE Cash (
    Payment_ID INT PRIMARY KEY,
    Receipt_Number VARCHAR(100),
    FOREIGN KEY (Payment_ID) REFERENCES Payment(Payment_ID)
);

CREATE TABLE Credit_Card (
    Payment_ID INT PRIMARY KEY,
    Card_Number VARCHAR(20),
    CVV VARCHAR(5),
    FOREIGN KEY (Payment_ID) REFERENCES Payment(Payment_ID)
);

CREATE TABLE On_line (
    Payment_ID INT PRIMARY KEY,
    Transaction_Code VARCHAR(50),
    FOREIGN KEY (Payment_ID) REFERENCES Payment(Payment_ID)
);

-- ========== Refund ==========
CREATE TABLE Refund (
    Refund_ID INT PRIMARY KEY,
    Payment_ID INT,
    Amount DECIMAL(10,2),
    Status_s VARCHAR(50),
    FOREIGN KEY (Payment_ID) REFERENCES Payment(Payment_ID)
);

-- ========== Delivery Order ==========
CREATE TABLE Delivery_Order (
    Order_ID INT PRIMARY KEY,
    Delivery_fee DECIMAL(10,2),
    D_Employee_ID INT,
    FOREIGN KEY (Order_ID) REFERENCES Orders(Order_ID),
    FOREIGN KEY (D_Employee_ID) REFERENCES Delivery_Boy(Employee_ID)
);
ALTER TABLE Payment ADD COLUMN Amount DECIMAL(10,2) AFTER Total_payment;
UPDATE Payment SET Amount = Total_payment;
-- ===============================
--  SAMPLE DATA
-- ===============================

-- Insert Menu
INSERT INTO Menu (Menu_ID) VALUES (1);

-- Insert Restaurant
INSERT INTO Restaurant (Restaurant_ID, Email, Phone, Street, City, Opening_Hours, Closing_Hours, Menu_ID)
VALUES (1, 'info@foodie.com', '1234567890', 'Main St', 'FoodTown', '09:00:00', '23:00:00', 1);

-- Insert Delivery Areas
INSERT INTO Delivery_Area (Area_code, City, Street) VALUES 
('A1', 'FoodTown', 'Main St'),
('A2', 'FoodTown', 'Second St');

-- Insert Employees
INSERT INTO Employee (Employee_ID, Employee_FirstName, Employee_LastName, Salary, Phone, Role, Username, PasswordHash, Email)
VALUES 
(1, 'John', 'Doe', 2500.00, '1234567890', 'D', 'john.doe', 'hashedpassword1', 'john@foodie.com'),
(2, 'Alice', 'Smith', 2200.00, '0987654321', 'C', 'alice.smith', 'hashedpassword2', 'alice@foodie.com');

-- Insert Delivery_Boy
INSERT INTO Delivery_Boy (Employee_ID, Availability, Order_ID)
VALUES (1, TRUE, NULL);

-- Insert Assignment (junction)
INSERT INTO Delivery_Assignment (Employee_ID, Area_Code) VALUES (1, 'A1'), (1, 'A2');

-- Insert Menu Items
INSERT INTO Menu_Item (Item_ID, Menu_ID, Name, Description, Category, Price, Is_Available)
VALUES
(1, 1, 'Burger', 'Beef burger with cheese', 'Main', 5.99, TRUE),
(2, 1, 'Fries', 'Crispy potato fries', 'Sides', 2.99, TRUE);

-- Insert Customers
INSERT INTO Customer VALUES
(1, 'Ahmed', 'Mohamed', 'ahmed.mohamed@example.com', 'Tahrir Street', '12', 'Cairo', 'R', '0123456789'),
(2, 'Fatma', 'Hassan', 'fatma.hassan@example.com', 'El Nasr Road', '23B', 'Nasr City', 'P', '0123456790'),
(3, 'Youssef', 'Ali', 'youssef.ali@example.com', 'Corniche El Nile', '45', 'Giza', 'R', '0123456791'),
(4, 'Mona', 'Khaled', 'mona.khaled@example.com', 'Al Haram Street', '56', 'Giza', 'P', '0123456792'),
(5, 'Omar', 'Fathy', 'omar.fathy@example.com', 'Makram Ebeid', '78', 'Nasr City', 'R', '0123456793');

-- Insert Regular and Premium Customers
INSERT INTO Regular_Customer VALUES (1), (3), (5);
INSERT INTO Premium_Customer VALUES (2, 0.10), (4, 0.15);

-- Insert Orders
INSERT INTO Orders (Order_ID, Order_Time, Status, Customer_ID, Restaurant_ID, Order_Type)
VALUES 
(1, NOW(), 'Confirmed', 1, 1, 'Delivery'),
(2, NOW(), 'Completed', 2, 1, 'InDine'),
(3, NOW(), 'Pending', 3, 1, 'Delivery');

-- Insert Order Items
INSERT INTO contains (Order_ID, Item_ID, Quantity) VALUES 
(1, 1, 1),
(2, 1, 1), (2, 2, 2),
(3, 2, 1);

-- Insert Payment
INSERT INTO Payment (Payment_ID, Total_payment, Order_ID, Payment_method,Payment_Date)
VALUES 
(1, 5.99, 1, 'OL','2023-06-15'),
(2, 8.98, 2, 'CC','2023-06-15'),
(3, 2.99, 3, 'Ca','2023-06-15');

INSERT INTO On_line (Payment_ID, Transaction_Code) VALUES (1, 'TXN123456');
INSERT INTO Credit_Card (Payment_ID, Card_Number, CVV) VALUES (2, '4111111111111111', '123');
INSERT INTO Cash (Payment_ID, Receipt_Number) VALUES (3, 'CASH-789012');

-- Insert InDine and Delivery Orders
INSERT INTO InDine_Order (Order_ID, Table_number) VALUES (2, 5);
INSERT INTO Delivery_Order (Order_ID, Delivery_fee, D_Employee_ID) VALUES 
(1, 3.50, 1),
(3, 2.50, 1);

-- Insert History
INSERT INTO Customer_History (History_ID, Customer_ID, Order_ID, Date_Visited, Feedback)
VALUES 
(1, 1, 1, NOW(), 'Great food!'),
(2, 2, 2, NOW(), 'Excellent service'),
(3, 3, 3, NOW(), NULL);

-- Insert User Login
INSERT INTO UserLogin (username, password) VALUES ('admin', 'admin123');







-- ===============================
-- Additional Sample Data for RestaurantDB1
-- ===============================

-- Insert more Menus
INSERT INTO Menu (Menu_ID) VALUES 
(2), (3), (4), (5);

-- Insert more Restaurants
INSERT INTO Restaurant (Restaurant_ID, Email, Phone, Street, City, Opening_Hours, Closing_Hours, Menu_ID)
VALUES 
(2, 'downtown@foodie.com', '2345678901', 'Central Ave', 'FoodTown', '08:00:00', '22:00:00', 2),
(3, 'uptown@foodie.com', '3456789012', 'North St', 'FoodTown', '10:00:00', '23:30:00', 3),
(4, 'eastside@foodie.com', '4567890123', 'East Blvd', 'FoodTown', '07:00:00', '21:00:00', 4),
(5, 'westside@foodie.com', '5678901234', 'West Rd', 'FoodTown', '11:00:00', '00:00:00', 5);

-- Insert more Delivery Areas
INSERT INTO Delivery_Area (Area_code, City, Street) VALUES 
('A3', 'FoodTown', 'Third Ave'),
('A4', 'FoodTown', 'Park Lane'),
('A5', 'FoodTown', 'Market St'),
('B1', 'BurgerCity', 'Main St'),
('B2', 'BurgerCity', 'Central Ave');

-- Insert more Employees
INSERT INTO Employee (Employee_ID, Employee_FirstName, Employee_LastName, Salary, Phone, Role, Username, PasswordHash, Email)
VALUES 
(4, 'Emily', 'Williams', 2600.00, '2233445566', 'W', 'emily.w', 'hashedpass4', 'emily@foodie.com'),
(5, 'Michael', 'Brown', 3000.00, '3344556677', 'C', 'michael.b', 'hashedpass5', 'michael@foodie.com'),
(6, 'Sarah', 'Davis', 2700.00, '4455667788', 'D', 'sarah.d', 'hashedpass6', 'sarah@foodie.com'),
(7, 'David', 'Miller', 2900.00, '5566778899', 'C', 'david.m', 'hashedpass7', 'david@foodie.com'),
(8, 'Jennifer', 'Wilson', 2400.00, '6677889900', 'W', 'jennifer.w', 'hashedpass8', 'jennifer@foodie.com'),
(9, 'James', 'Moore', 3100.00, '7788990011', 'C', 'james.m', 'hashedpass9', 'james@foodie.com'),
(10, 'Jessica', 'Taylor', 2500.00, '8899001122', 'D', 'jessica.t', 'hashedpass10', 'jessica@foodie.com');

-- Insert more Delivery_Boys
INSERT INTO Delivery_Boy (Employee_ID, Availability, Order_ID)
VALUES 
(6, TRUE, NULL),
(10, FALSE, NULL);

-- Insert more Assignments
INSERT INTO Delivery_Assignment (Employee_ID, Area_Code) VALUES 
(1, 'A3'), (1, 'A4'),
(6, 'A2'), (6, 'A5'),
(10, 'B1'), (10, 'B2');



-- Insert more Chefs
INSERT INTO Chef (Employee_ID, Specialty)
VALUES 
(2, 'Italian Cuisine'),
(5, 'Grill Master'),
(7, 'Pastry Chef'),
(9, 'Sushi Chef');

-- Insert more Menu Items
INSERT INTO Menu_Item (Item_ID, Menu_ID, Name, Description, Category, Price, Is_Available)
VALUES
(3, 1, 'Pizza', 'Classic Margherita pizza', 'Main', 8.99, TRUE),
(4, 1, 'Salad', 'Fresh garden salad', 'Starter', 4.99, TRUE),
(5, 2, 'Steak', 'Grilled ribeye steak', 'Main', 15.99, TRUE),
(6, 2, 'Soup', 'Creamy tomato soup', 'Starter', 3.99, TRUE),
(7, 3, 'Pasta', 'Spaghetti Bolognese', 'Main', 10.99, TRUE),
(8, 3, 'Garlic Bread', 'Toasted with garlic butter', 'Side', 2.99, TRUE),
(9, 4, 'Sushi Platter', 'Assorted sushi selection', 'Main', 12.99, TRUE),
(10, 4, 'Miso Soup', 'Traditional Japanese soup', 'Starter', 2.99, TRUE),
(11, 5, 'Burrito', 'Beef and bean burrito', 'Main', 7.99, TRUE),
(12, 5, 'Nachos', 'Loaded with cheese and toppings', 'Starter', 5.99, TRUE),
(13, 1, 'Ice Cream', 'Vanilla ice cream', 'Dessert', 3.99, TRUE),
(14, 2, 'Cheesecake', 'New York style cheesecake', 'Dessert', 5.99, TRUE),
(15, 3, 'Tiramisu', 'Classic Italian dessert', 'Dessert', 6.99, TRUE),
(16, 4, 'Mochi', 'Japanese rice cake', 'Dessert', 4.99, TRUE),
(17, 5, 'Churros', 'Fried dough pastry', 'Dessert', 3.99, TRUE);

-- Insert more Customers
INSERT INTO Customer VALUES
(6, 'Layla', 'Mahmoud', 'layla.m@example.com', 'Garden City', '34', 'Cairo', 'P', '0123456794'),
(7, 'Karim', 'Ibrahim', 'karim.i@example.com', 'Zamalek', '67', 'Cairo', 'R', '0123456795'),
(8, 'Nour', 'Samir', 'nour.s@example.com', 'Heliopolis', '89', 'Cairo', 'P', '0123456796'),
(9, 'Hassan', 'Farouk', 'hassan.f@example.com', 'Maadi', '101', 'Cairo', 'R', '0123456797'),
(10, 'Dalia', 'Youssef', 'dalia.y@example.com', 'Dokki', '112', 'Giza', 'P', '0123456798'),
(11, 'Tarek', 'Nasser', 'tarek.n@example.com', '6th October', '131', 'Giza', 'R', '0123456799'),
(12, 'Amina', 'Kamal', 'amina.k@example.com', 'Sheikh Zayed', '415', 'Giza', 'P', '0123456800'),
(13, 'Samir', 'Adel', 'samir.a@example.com', 'New Cairo', '516', 'Cairo', 'R', '0123456801'),
(14, 'Hana', 'Osman', 'hana.o@example.com', 'Nasr City', '617', 'Cairo', 'P', '0123456802'),
(15, 'Yasin', 'Hamdi', 'yasin.h@example.com', 'Mohandessin', '718', 'Giza', 'R', '0123456803');

-- Insert more Regular and Premium Customers
INSERT INTO Regular_Customer VALUES (7), (9), (11), (13), (15);
INSERT INTO Premium_Customer VALUES (6, 0.12), (8, 0.15), (10, 0.10), (12, 0.20), (14, 0.18);

-- Insert more Customer Phones
INSERT INTO Customer_Phone (Customer_ID, Phone_Number) VALUES
(1, '01012345678'),
(1, '01123456789'),
(2, '01098765432'),
(3, '01187654321'),
(4, '01055556666'),
(5, '01199998888'),
(6, '01011112222'),
(7, '01133334444'),
(8, '01066667777'),
(9, '01188889999'),
(10, '01022223333'),
(11, '01144445555'),
(12, '01077778888'),
(13, '01100001111'),
(14, '01012123434'),
(15, '01134345656');



-- Insert more Restaurant Phones
INSERT INTO Restaurant_Phone (Restaurant_ID, Phone) VALUES
(1, '0223456789'),
(1, '0223456790'),
(2, '0224567890'),
(3, '0225678901'),
(4, '0226789012'),
(5, '0227890123');

-- Insert more geo_Locations
INSERT INTO geo_Location (geo_Location_ID, Restaurant_ID, Latitude, Longitude) VALUES
(1, 1, 30.0444, 31.2357),
(2, 2, 30.0455, 31.2368),
(3, 3, 30.0466, 31.2379),
(4, 4, 30.0477, 31.2380),
(5, 5, 30.0488, 31.2391);

-- Insert more Covered_by relationships
INSERT INTO Covered_by (geo_Location_ID, Restaurant_ID, Area_Code) VALUES
(1, 1, 'A1'),
(1, 1, 'A2'),
(2, 2, 'A3'),
(3, 3, 'A4'),
(4, 4, 'A5'),
(5, 5, 'B1');

-- Insert more Orders
INSERT INTO Orders (Order_ID, Order_Time, Status, Customer_ID, Restaurant_ID, Order_Type)
VALUES 
(4, '2023-05-15 12:30:00', 'Completed', 6, 2, 'InDine'),
(5, '2023-05-15 13:45:00', 'Completed', 7, 3, 'Delivery'),
(6, '2023-05-16 18:00:00', 'Completed', 8, 1, 'InDine'),
(7, '2023-05-16 19:30:00', 'Cancelled', 9, 4, 'Delivery'),
(8, '2023-05-17 11:15:00', 'Completed', 10, 5, 'InDine'),
(9, '2023-05-17 12:45:00', 'Completed', 11, 2, 'Delivery'),
(10, '2023-05-18 14:00:00', 'Processing', 12, 3, 'InDine'),
(11, '2023-05-18 20:30:00', 'Completed', 13, 4, 'Delivery'),
(12, '2023-05-19 12:00:00', 'Completed', 14, 5, 'InDine'),
(13, '2023-05-19 19:45:00', 'Processing', 15, 1, 'Delivery'),
(14, '2023-05-20 13:15:00', 'Completed', 1, 2, 'InDine'),
(15, '2023-05-20 18:30:00', 'Completed', 2, 3, 'Delivery');

-- Insert more Order Items
INSERT INTO contains (Order_ID, Item_ID) VALUES 
(4, 5), (4, 6),
(5, 7), (5, 8),
(6, 3), (6, 4),
(7, 9), (7, 10),
(8, 11), (8, 12),
(9, 5), (9, 14),
(10, 7), (10, 8), (10, 15),
(11, 9), (11, 16),
(12, 11), (12, 17),
(13, 1), (13, 2), (13, 13),
(14, 5), (14, 6), (14, 14),
(15, 7), (15, 15);

-- Insert more InDine Orders
INSERT INTO InDine_Order (Order_ID, Table_number) VALUES 
(4, 7),
(6, 2),
(8, 3),
(10, 4),
(12, 5),
(14, 1);

-- Insert more Delivery Orders
INSERT INTO Delivery_Order (Order_ID, Delivery_fee, D_Employee_ID) VALUES 
(5, 4.50, 6),
(7, 3.50, 10),
(9, 5.00, 1),
(11, 4.00, 6),
(13, 3.00, 10),
(15, 4.50, 1);

-- Insert more Payments
INSERT INTO Payment (Payment_ID, Total_payment, Order_ID, Payment_method)
VALUES 
(4, 20.98, 4, 'CC'),
(5, 13.98, 5, 'OL'),
(6, 13.98, 6, 'Ca'),
(7, 15.98, 7, 'CC'),
(8, 13.98, 8, 'OL'),
(9, 21.98, 9, 'Ca'),
(10, 20.97, 10, 'CC'),
(11, 17.98, 11, 'OL'),
(12, 13.98, 12, 'Ca'),
(13, 12.97, 13, 'CC'),
(14, 26.97, 14, 'OL'),
(15, 17.98, 15, 'Ca');

-- Insert more Payment details
INSERT INTO Credit_Card (Payment_ID, Card_Number, CVV) VALUES 
(4, '5555666677778888', '456'),
(7, '6666777788889999', '789'),
(10, '7777888899990000', '012'),
(13, '8888999900001111', '345');

INSERT INTO On_line (Payment_ID, Transaction_Code) VALUES 
(5, 'TXN789012'),
(8, 'TXN345678'),
(11, 'TXN901234'),
(14, 'TXN567890');

INSERT INTO Cash (Payment_ID, Receipt_Number) VALUES 
(6, 'CASH-345678'),
(9, 'CASH-901234'),
(12, 'CASH-567890'),
(15, 'CASH-123456');

-- Insert more Customer History
INSERT INTO Customer_History (History_ID, Customer_ID, Order_ID, Date_Visited, Feedback)
VALUES 
(4, 6, 4, '2023-05-15 13:30:00', 'Excellent food quality'),
(5, 7, 5, '2023-05-15 14:30:00', 'Fast delivery'),
(6, 8, 6, '2023-05-16 19:00:00', 'Friendly staff'),
(7, 9, 7, '2023-05-16 20:00:00', 'Order was cancelled without notice'),
(8, 10, 8, '2023-05-17 12:15:00', 'Great atmosphere'),
(9, 11, 9, '2023-05-17 13:30:00', 'Food arrived cold'),
(10, 12, 10, '2023-05-18 15:00:00', 'Will come again'),
(11, 13, 11, '2023-05-18 21:15:00', 'Perfect sushi'),
(12, 14, 12, '2023-05-19 13:00:00', 'Best Mexican in town'),
(13, 15, 13, '2023-05-19 20:30:00', 'Good but took too long'),
(14, 1, 14, '2023-05-20 14:15:00', 'Steak was perfectly cooked'),
(15, 2, 15, '2023-05-20 19:15:00', 'Pasta was delicious');

-- Insert more User Logins
INSERT INTO UserLogin (username, password, email) VALUES 
('manager1', 'managerpass1', 'manager1@foodie.com'),
('manager2', 'managerpass2', 'manager2@foodie.com'),
('chef1', 'chefpass1', 'chef1@foodie.com'),
('chef2', 'chefpass2', 'chef2@foodie.com'),
('waiter1', 'waiterpass1', 'waiter1@foodie.com'),
('waiter2', 'waiterpass2', 'waiter2@foodie.com'),
('delivery1', 'deliverypass1', 'delivery1@foodie.com'),
('delivery2', 'deliverypass2', 'delivery2@foodie.com'),
('customer1', 'customerpass1', 'customer1@foodie.com'),
('customer2', 'customerpass2', 'customer2@foodie.com');

-- Insert Refunds
INSERT INTO Refund (Refund_ID, Payment_ID, Amount, Status_s)
VALUES 
(1, 7, 15.98, 'Completed'),
(2, 9, 10.00, 'Pending');
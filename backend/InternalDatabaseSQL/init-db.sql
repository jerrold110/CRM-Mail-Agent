-- For agent memory
CREATE DATABASE agent_memory;

-- Create the shoe_characteristics table
CREATE TABLE public.shoe_characteristics (
    product_id INT PRIMARY KEY,
    product_name TEXT NOT NULL,
    size DECIMAL(3,1) NOT NULL CHECK (size > 0),
    color VARCHAR(50) NOT NULL,
    material VARCHAR(50),
    weight DECIMAL(5,2) CHECK (weight > 0),
    brand VARCHAR(100),
    price DECIMAL(10,2) CHECK (price >= 0),
    description TEXT
);

-- Insert data into shoe_characteristics table
INSERT INTO public.shoe_characteristics (
    product_id, product_name, size, color, material, weight, brand, price, description
)
VALUES
    (1, 'Nike Air Max', 10.0, 'Red', 'Leather', 0.80, 'Nike', 129.99, 'The Nike Air Max offers great cushioning and stylish design.'),
    (2, 'Nike Air Max', 9.5, 'Red', 'Leather', 0.80, 'Nike', 129.99, 'The Nike Air Max offers great cushioning and stylish design.'),
    (3, 'Adidas Ultraboost', 10.0, 'Black', 'Mesh', 0.70, 'Adidas', 180.00, 'The Adidas Ultraboost is known for its comfort and breathability.'),
    (4, 'Adidas Ultraboost', 9.5, 'Black', 'Mesh', 0.70, 'Adidas', 180.00, 'The Adidas Ultraboost is known for its comfort and breathability.'),
    (5, 'Puma RS-X', 10.0, 'Blue', 'Synthetic', 0.90, 'Puma', 110.00, 'The Puma RS-X combines bold styling with durable performance.'),
    (6, 'Puma RS-X', 9.5, 'Blue', 'Synthetic', 0.90, 'Puma', 110.00, 'The Puma RS-X combines bold styling with durable performance.'),
    (7, 'Puma RS-X', 9.5, 'Red', 'Synthetic', 0.90, 'Puma', 110.00, 'The Puma RS-X combines bold styling with durable performance.'),
    (8, 'Nike Air Max', 11.0, 'Red', 'Leather', 0.80, 'Nike', 129.99, 'The Nike Air Max offers great cushioning and stylish design.'),
    (9, 'Nike Air Max', 8.5, 'Blue', 'Leather', 0.80, 'Nike', 129.99, 'The Nike Air Max offers great cushioning and stylish design.'),
    (10, 'Nike Air Max', 10.0, 'White', 'Leather', 0.80, 'Nike', 129.99, 'The Nike Air Max offers great cushioning and stylish design.'),
    (11, 'Adidas Ultraboost', 11.0, 'Black', 'Mesh', 0.70, 'Adidas', 180.00, 'The Adidas Ultraboost is known for its comfort and breathability.'),
    (12, 'Adidas Ultraboost', 8.5, 'White', 'Mesh', 0.70, 'Adidas', 180.00, 'The Adidas Ultraboost is known for its comfort and breathability.'),
    (13, 'Adidas Ultraboost', 10.0, 'Grey', 'Mesh', 0.70, 'Adidas', 180.00, 'The Adidas Ultraboost is known for its comfort and breathability.'),
    (14, 'Puma RS-X', 11.0, 'Blue', 'Synthetic', 0.90, 'Puma', 110.00, 'The Puma RS-X combines bold styling with durable performance.'),
    (15, 'Puma RS-X', 8.5, 'Red', 'Synthetic', 0.90, 'Puma', 110.00, 'The Puma RS-X combines bold styling with durable performance.'),
    (16, 'Puma RS-X', 10.0, 'White', 'Synthetic', 0.90, 'Puma', 110.00, 'The Puma RS-X combines bold styling with durable performance.'),
    (17, 'Reebok Classic', 10.0, 'White', 'Leather', 0.75, 'Reebok', 85.00, 'The Reebok Classic delivers timeless style and everyday comfort.'),
    (18, 'Reebok Classic', 9.5, 'White', 'Leather', 0.75, 'Reebok', 85.00, 'The Reebok Classic delivers timeless style and everyday comfort.'),
    (19, 'Reebok Classic', 11.0, 'Black', 'Leather', 0.75, 'Reebok', 85.00, 'The Reebok Classic delivers timeless style and everyday comfort.'),
    (20, 'Reebok Classic', 8.5, 'Grey', 'Leather', 0.75, 'Reebok', 85.00, 'The Reebok Classic delivers timeless style and everyday comfort.'),
    (21, 'New Balance 990', 10.0, 'Grey', 'Suede', 0.85, 'New Balance', 175.00, 'The New Balance 990 is a premium running shoe with superior cushioning.'),
    (22, 'New Balance 990', 9.5, 'Grey', 'Suede', 0.85, 'New Balance', 175.00, 'The New Balance 990 is a premium running shoe with superior cushioning.'),
    (23, 'New Balance 990', 11.0, 'Navy', 'Suede', 0.85, 'New Balance', 175.00, 'The New Balance 990 is a premium running shoe with superior cushioning.'),
    (24, 'New Balance 990', 8.5, 'Black', 'Suede', 0.85, 'New Balance', 175.00, 'The New Balance 990 is a premium running shoe with superior cushioning.'),
    (25, 'Converse Chuck Taylor', 10.0, 'Black', 'Canvas', 0.60, 'Converse', 65.00, 'The Converse Chuck Taylor is an iconic sneaker loved worldwide.'),
    (26, 'Converse Chuck Taylor', 9.5, 'Red', 'Canvas', 0.60, 'Converse', 65.00, 'The Converse Chuck Taylor is an iconic sneaker loved worldwide.'),
    (27, 'Converse Chuck Taylor', 11.0, 'White', 'Canvas', 0.60, 'Converse', 65.00, 'The Converse Chuck Taylor is an iconic sneaker loved worldwide.'),
    (28, 'Converse Chuck Taylor', 8.5, 'Navy', 'Canvas', 0.60, 'Converse', 65.00, 'The Converse Chuck Taylor is an iconic sneaker loved worldwide.'),
    (29, 'Vans Old Skool', 10.0, 'Black', 'Canvas', 0.65, 'Vans', 70.00, 'The Vans Old Skool features classic skate style and durability.'),
    (30, 'Vans Old Skool', 9.5, 'Black', 'Canvas', 0.65, 'Vans', 70.00, 'The Vans Old Skool features classic skate style and durability.'),
    (31, 'Vans Old Skool', 11.0, 'Navy', 'Canvas', 0.65, 'Vans', 70.00, 'The Vans Old Skool features classic skate style and durability.'),
    (32, 'Vans Old Skool', 8.5, 'Red', 'Canvas', 0.65, 'Vans', 70.00, 'The Vans Old Skool features classic skate style and durability.'),
    (33, 'Asics Gel-Kayano', 10.0, 'Blue', 'Mesh', 0.80, 'Asics', 160.00, 'The Asics Gel-Kayano provides exceptional stability and support.'),
    (34, 'Asics Gel-Kayano', 9.5, 'Black', 'Mesh', 0.80, 'Asics', 160.00, 'The Asics Gel-Kayano provides exceptional stability and support.'),
    (35, 'Asics Gel-Kayano', 11.0, 'Grey', 'Mesh', 0.80, 'Asics', 160.00, 'The Asics Gel-Kayano provides exceptional stability and support.'),
    (36, 'Asics Gel-Kayano', 8.5, 'White', 'Mesh', 0.80, 'Asics', 160.00, 'The Asics Gel-Kayano provides exceptional stability and support.'),
    (37, 'Under Armour HOVR', 10.0, 'Black', 'Knit', 0.75, 'Under Armour', 140.00, 'The Under Armour HOVR delivers energy return and smooth ride.'),
    (38, 'Under Armour HOVR', 9.5, 'Red', 'Knit', 0.75, 'Under Armour', 140.00, 'The Under Armour HOVR delivers energy return and smooth ride.'),
    (39, 'Under Armour HOVR', 11.0, 'White', 'Knit', 0.75, 'Under Armour', 140.00, 'The Under Armour HOVR delivers energy return and smooth ride.'),
    (40, 'Under Armour HOVR', 8.5, 'Grey', 'Knit', 0.75, 'Under Armour', 140.00, 'The Under Armour HOVR delivers energy return and smooth ride.'),
    (41, 'Saucony Ride', 10.0, 'Blue', 'Mesh', 0.72, 'Saucony', 130.00, 'The Saucony Ride offers smooth transitions and responsive cushioning.'),
    (42, 'Saucony Ride', 9.5, 'Black', 'Mesh', 0.72, 'Saucony', 130.00, 'The Saucony Ride offers smooth transitions and responsive cushioning.'),
    (43, 'Saucony Ride', 11.0, 'Orange', 'Mesh', 0.72, 'Saucony', 130.00, 'The Saucony Ride offers smooth transitions and responsive cushioning.'),
    (44, 'Saucony Ride', 8.5, 'Grey', 'Mesh', 0.72, 'Saucony', 130.00, 'The Saucony Ride offers smooth transitions and responsive cushioning.'),
    (45, 'Brooks Ghost', 10.0, 'Black', 'Mesh', 0.78, 'Brooks', 150.00, 'The Brooks Ghost is a versatile neutral running shoe.'),
    (46, 'Brooks Ghost', 9.5, 'Blue', 'Mesh', 0.78, 'Brooks', 150.00, 'The Brooks Ghost is a versatile neutral running shoe.'),
    (47, 'Brooks Ghost', 11.0, 'White', 'Mesh', 0.78, 'Brooks', 150.00, 'The Brooks Ghost is a versatile neutral running shoe.'),
    (48, 'Brooks Ghost', 8.5, 'Grey', 'Mesh', 0.78, 'Brooks', 150.00, 'The Brooks Ghost is a versatile neutral running shoe.'),
    (49, 'Hoka Clifton', 10.0, 'White', 'Mesh', 0.68, 'Hoka', 145.00, 'The Hoka Clifton is lightweight with maximum cushioning.'),
    (50, 'Hoka Clifton', 9.5, 'Black', 'Mesh', 0.68, 'Hoka', 145.00, 'The Hoka Clifton is lightweight with maximum cushioning.'),
    (51, 'Hoka Clifton', 11.0, 'Blue', 'Mesh', 0.68, 'Hoka', 145.00, 'The Hoka Clifton is lightweight with maximum cushioning.'),
    (52, 'Hoka Clifton', 8.5, 'Grey', 'Mesh', 0.68, 'Hoka', 145.00, 'The Hoka Clifton is lightweight with maximum cushioning.'),
    (53, 'Salomon Speedcross', 10.0, 'Black', 'Synthetic', 0.82, 'Salomon', 135.00, 'The Salomon Speedcross excels in trail running performance.'),
    (54, 'Salomon Speedcross', 9.5, 'Blue', 'Synthetic', 0.82, 'Salomon', 135.00, 'The Salomon Speedcross excels in trail running performance.'),
    (55, 'Salomon Speedcross', 11.0, 'Red', 'Synthetic', 0.82, 'Salomon', 135.00, 'The Salomon Speedcross excels in trail running performance.'),
    (56, 'Salomon Speedcross', 8.5, 'Grey', 'Synthetic', 0.82, 'Salomon', 135.00, 'The Salomon Speedcross excels in trail running performance.'),
    (57, 'Mizuno Wave Rider', 10.0, 'Blue', 'Mesh', 0.76, 'Mizuno', 125.00, 'The Mizuno Wave Rider provides smooth and stable rides.'),
    (58, 'Mizuno Wave Rider', 9.5, 'Black', 'Mesh', 0.76, 'Mizuno', 125.00, 'The Mizuno Wave Rider provides smooth and stable rides.'),
    (59, 'Mizuno Wave Rider', 11.0, 'White', 'Mesh', 0.76, 'Mizuno', 125.00, 'The Mizuno Wave Rider provides smooth and stable rides.'),
    (60, 'Mizuno Wave Rider', 8.5, 'Orange', 'Mesh', 0.76, 'Mizuno', 125.00, 'The Mizuno Wave Rider provides smooth and stable rides.');


-- Create the inventory table
CREATE TABLE public.inventory (
    product_id INT NOT NULL PRIMARY KEY,
    product_name TEXT NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),

    CONSTRAINT fk_inventory_shoe
        FOREIGN KEY (product_id)
        REFERENCES public.shoe_characteristics(product_id)
        ON DELETE CASCADE
);

-- Insert data into inventory table
INSERT INTO public.inventory (
    product_id, product_name, quantity
)
VALUES
    (1, 'Nike Air Max', 100),
    (2, 'Nike Air Max', 100),
    (3, 'Adidas Ultraboost', 0),
    (4, 'Adidas Ultraboost', 0),
    (5, 'Puma RS-X', 90),
    (6, 'Puma RS-X', 90),
    (7, 'Puma RS-X', 75),
    (8, 'Nike Air Max', 85),
    (9, 'Nike Air Max', 95),
    (10, 'Nike Air Max', 110),
    (11, 'Adidas Ultraboost', 45),
    (12, 'Adidas Ultraboost', 50),
    (13, 'Adidas Ultraboost', 60),
    (14, 'Puma RS-X', 80),
    (15, 'Puma RS-X', 70),
    (16, 'Puma RS-X', 85),
    (17, 'Reebok Classic', 120),
    (18, 'Reebok Classic', 115),
    (19, 'Reebok Classic', 105),
    (20, 'Reebok Classic', 95),
    (21, 'New Balance 990', 65),
    (22, 'New Balance 990', 70),
    (23, 'New Balance 990', 55),
    (24, 'New Balance 990', 60),
    (25, 'Converse Chuck Taylor', 150),
    (26, 'Converse Chuck Taylor', 145),
    (27, 'Converse Chuck Taylor', 140),
    (28, 'Converse Chuck Taylor', 135),
    (29, 'Vans Old Skool', 130),
    (30, 'Vans Old Skool', 125),
    (31, 'Vans Old Skool', 120),
    (32, 'Vans Old Skool', 115),
    (33, 'Asics Gel-Kayano', 75),
    (34, 'Asics Gel-Kayano', 80),
    (35, 'Asics Gel-Kayano', 70),
    (36, 'Asics Gel-Kayano', 65),
    (37, 'Under Armour HOVR', 90),
    (38, 'Under Armour HOVR', 85),
    (39, 'Under Armour HOVR', 95),
    (40, 'Under Armour HOVR', 80),
    (41, 'Saucony Ride', 100),
    (42, 'Saucony Ride', 105),
    (43, 'Saucony Ride', 95),
    (44, 'Saucony Ride', 90),
    (45, 'Brooks Ghost', 85),
    (46, 'Brooks Ghost', 80),
    (47, 'Brooks Ghost', 90),
    (48, 'Brooks Ghost', 75),
    (49, 'Hoka Clifton', 110),
    (50, 'Hoka Clifton', 115),
    (51, 'Hoka Clifton', 105),
    (52, 'Hoka Clifton', 100),
    (53, 'Salomon Speedcross', 70),
    (54, 'Salomon Speedcross', 75),
    (55, 'Salomon Speedcross', 65),
    (56, 'Salomon Speedcross', 60),
    (57, 'Mizuno Wave Rider', 95),
    (58, 'Mizuno Wave Rider', 100),
    (59, 'Mizuno Wave Rider', 90),
    (60, 'Mizuno Wave Rider', 85);


-- Create the incoming_deliveries table
CREATE TABLE public.incoming_deliveries (
    delivery_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    expected_date DATE NOT NULL,
    received_date DATE,
    supplier VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending | received | cancelled

    CONSTRAINT fk_delivery_shoe
        FOREIGN KEY (product_id)
        REFERENCES public.shoe_characteristics(product_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_delivery_status
        CHECK (status IN ('pending', 'received', 'cancelled')),

    CONSTRAINT chk_received_date
        CHECK (
            received_date IS NULL
            OR received_date >= expected_date
        )
);

-- Insert data into incoming_deliveries table
INSERT INTO public.incoming_deliveries (
    product_id, quantity, expected_date, supplier
)
VALUES
    (1, 50, '2026-01-15', 'Nike Distributor'),
    (2, 50, '2026-01-15', 'Nike Distributor'),
    (3, 30, '2026-01-20', 'Adidas Warehouse'),
    (3, 30, '2026-01-20', 'Adidas Warehouse'),
    (4, 40, '2026-01-25', 'Adidas Warehouse'),
    (5, 35, '2026-02-01', 'Puma Supply Chain'),
    (6, 35, '2026-02-01', 'Puma Supply Chain'),
    (7, 25, '2026-02-05', 'Puma Supply Chain'),
    (8, 45, '2026-02-10', 'Nike Distributor'),
    (9, 40, '2026-02-10', 'Nike Distributor'),
    (10, 50, '2026-02-15', 'Nike Distributor'),
    (11, 30, '2026-02-20', 'Adidas Warehouse'),
    (12, 35, '2026-02-20', 'Adidas Warehouse'),
    (13, 40, '2026-02-25', 'Adidas Warehouse'),
    (14, 30, '2026-03-01', 'Puma Supply Chain'),
    (15, 25, '2026-03-01', 'Puma Supply Chain'),
    (16, 35, '2026-03-05', 'Puma Supply Chain'),
    (17, 60, '2026-03-10', 'Reebok Logistics'),
    (18, 55, '2026-03-10', 'Reebok Logistics'),
    (19, 50, '2026-03-15', 'Reebok Logistics'),
    (20, 45, '2026-03-15', 'Reebok Logistics'),
    (21, 35, '2026-03-20', 'New Balance Central'),
    (22, 40, '2026-03-20', 'New Balance Central'),
    (23, 30, '2026-03-25', 'New Balance Central'),
    (24, 35, '2026-03-25', 'New Balance Central'),
    (25, 75, '2026-04-01', 'Converse Wholesale'),
    (26, 70, '2026-04-01', 'Converse Wholesale'),
    (27, 65, '2026-04-05', 'Converse Wholesale'),
    (28, 60, '2026-04-05', 'Converse Wholesale'),
    (29, 55, '2026-04-10', 'Vans Distribution'),
    (30, 50, '2026-04-10', 'Vans Distribution'),
    (31, 55, '2026-04-15', 'Vans Distribution'),
    (32, 50, '2026-04-15', 'Vans Distribution'),
    (33, 40, '2026-04-20', 'Asics Regional'),
    (34, 45, '2026-04-20', 'Asics Regional'),
    (35, 35, '2026-04-25', 'Asics Regional'),
    (36, 40, '2026-04-25', 'Asics Regional'),
    (37, 45, '2026-05-01', 'Under Armour Direct'),
    (38, 40, '2026-05-01', 'Under Armour Direct'),
    (39, 50, '2026-05-05', 'Under Armour Direct'),
    (40, 45, '2026-05-05', 'Under Armour Direct'),
    (41, 50, '2026-05-10', 'Saucony Warehouse'),
    (42, 55, '2026-05-10', 'Saucony Warehouse'),
    (43, 45, '2026-05-15', 'Saucony Warehouse'),
    (44, 50, '2026-05-15', 'Saucony Warehouse'),
    (45, 40, '2026-05-20', 'Brooks Fulfillment'),
    (46, 45, '2026-05-20', 'Brooks Fulfillment'),
    (47, 50, '2026-05-25', 'Brooks Fulfillment'),
    (48, 40, '2026-05-25', 'Brooks Fulfillment'),
    (49, 55, '2026-06-01', 'Hoka Supply'),
    (50, 60, '2026-06-01', 'Hoka Supply'),
    (51, 50, '2026-06-05', 'Hoka Supply'),
    (52, 55, '2026-06-05', 'Hoka Supply'),
    (53, 35, '2026-06-10', 'Salomon Depot'),
    (54, 40, '2026-06-10', 'Salomon Depot'),
    (55, 30, '2026-06-15', 'Salomon Depot'),
    (56, 35, '2026-06-15', 'Salomon Depot'),
    (57, 45, '2026-06-20', 'Mizuno Center'),
    (58, 50, '2026-06-20', 'Mizuno Center'),
    (59, 40, '2026-06-25', 'Mizuno Center'),
    (60, 45, '2026-06-25', 'Mizuno Center');


-- Create the item_deliveries table
CREATE TABLE public.item_deliveries (
    delivery_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(200) NOT NULL,
    carrier VARCHAR(50),
    tracking_number VARCHAR(100),
    status VARCHAR(50) NOT NULL CHECK (status IN ('processing', 'in_transit', 'out_for_delivery', 'delivered', 'exception', 'cancelled')),
    expected_delivery_start DATE NOT NULL,
    expected_delivery_end DATE NOT NULL,
    actual_delivery_date DATE,
    shipped_date DATE,
    delivery_attempts INT DEFAULT 0
);

-- Insert data into item_deliveries table
-- Present date is January 29, 2026
INSERT INTO public.item_deliveries (
    delivery_id, order_id, customer_id, product_id, 
    origin, destination, carrier, tracking_number, status,
    expected_delivery_start, expected_delivery_end, actual_delivery_date, 
    shipped_date, delivery_attempts
) VALUES
    -- Delivered orders
    (1, 1001, 1, 1,
     'Warehouse A - California', '123 Main St, New York, NY 10001', 'FedEx', 'FDX123456789',
     'delivered', '2026-01-15', '2026-01-17', '2026-01-16', '2026-01-13', 0),
    
    (2, 1002, 2, 3,
     'Warehouse B - Texas', '456 Oak Ave, Seattle, WA 98101', 'UPS', 'UPS987654321',
     'delivered', '2026-01-16', '2026-01-18', '2026-01-17', '2026-01-14', 0),
    
    (3, 1003, 3, 5,
     'Warehouse A - California', '789 Pine Rd, Austin, TX 78701', 'USPS', 'USPS456789123',
     'delivered', '2026-01-10', '2026-01-12', '2026-01-15', '2026-01-08', 2),
    
    (4, 1004, 1, 7,
     'Warehouse B - Texas', '123 Main St, New York, NY 10001', 'FedEx', 'FDX111222333',
     'delivered', '2026-01-18', '2026-01-20', '2026-01-23', '2026-01-16', 1),
    
    (5, 1005, 4, 9,
     'Warehouse C - New Jersey', '321 Elm St, Miami, FL 33101', 'UPS', 'UPS555666777',
     'delivered', '2026-01-20', '2026-01-22', '2026-01-21', '2026-01-18', 0),
    
    (6, 1006, 5, 11,
     'Warehouse A - California', '654 Maple Dr, Portland, OR 97201', 'FedEx', 'FDX888999000',
     'delivered', '2026-01-19', '2026-01-21', '2026-01-20', '2026-01-17', 0),
    
    (7, 1007, 2, 13,
     'Warehouse B - Texas', '789 Pine Rd, Austin, TX 78701', 'USPS', 'USPS777888999',
     'delivered', '2026-01-17', '2026-01-19', '2026-01-22', '2026-01-15', 0),
    
    (8, 1008, 6, 15,
     'Warehouse C - New Jersey', '159 Birch Ln, Boston, MA 02101', 'UPS', 'UPS321654987',
     'delivered', '2026-01-20', '2026-01-22', '2026-01-22', '2026-01-18', 1),
    
    (9, 1009, 7, 17,
     'Warehouse A - California', '753 Cedar St, Denver, CO 80201', 'FedEx', 'FDX963852741',
     'delivered', '2026-01-14', '2026-01-16', '2026-01-15', '2026-01-12', 0),
    
    (10, 1010, 1, 19,
     'Warehouse B - Texas', '123 Main St, New York, NY 10001', 'UPS', 'UPS147258369',
     'delivered', '2026-01-21', '2026-01-23', '2026-01-22', '2026-01-19', 0),
    
    (11, 1011, 8, 21,
     'Warehouse C - New Jersey', '951 Spruce Ave, Chicago, IL 60601', 'FedEx', 'FDX741852963',
     'delivered', '2026-01-18', '2026-01-20', '2026-01-26', '2026-01-16', 2),
    
    (12, 1012, 9, 23,
     'Warehouse A - California', '357 Willow Way, San Diego, CA 92101', 'USPS', 'USPS951753468',
     'delivered', '2026-01-22', '2026-01-24', '2026-01-23', '2026-01-20', 0),
    
    (13, 1013, 10, 25,
     'Warehouse B - Texas', '159 Magnolia Ct, Houston, TX 77001', 'UPS', 'UPS852963741',
     'delivered', '2026-01-19', '2026-01-21', '2026-01-20', '2026-01-17', 0),
    
    (14, 1014, 11, 27,
     'Warehouse C - New Jersey', '753 Hickory Rd, Philadelphia, PA 19101', 'FedEx', 'FDX159357852',
     'delivered', '2026-01-23', '2026-01-25', '2026-01-24', '2026-01-21', 0),
    
    (15, 1015, 12, 29,
     'Warehouse A - California', '951 Poplar Ln, Phoenix, AZ 85001', 'USPS', 'USPS753951468',
     'delivered', '2026-01-20', '2026-01-22', '2026-01-25', '2026-01-18', 1),
    
    -- Out for delivery
    (16, 1016, 13, 31,
     'Warehouse B - Texas', '357 Sycamore Dr, Dallas, TX 75201', 'UPS', 'UPS456789012',
     'out_for_delivery', '2026-01-28', '2026-01-30', NULL, '2026-01-26', 0),
    
    (17, 1017, 14, 33,
     'Warehouse C - New Jersey', '159 Chestnut Ave, Baltimore, MD 21201', 'FedEx', 'FDX789456123',
     'out_for_delivery', '2026-01-29', '2026-01-31', NULL, '2026-01-27', 0),
    
    (18, 1018, 15, 35,
     'Warehouse A - California', '753 Redwood St, San Francisco, CA 94101', 'USPS', 'USPS147258369',
     'out_for_delivery', '2026-01-29', '2026-01-31', NULL, '2026-01-27', 1),
    
    -- In transit
    (19, 1019, 3, 37,
     'Warehouse B - Texas', '951 Oakmont Pl, Atlanta, GA 30301', 'UPS', 'UPS369258147',
     'in_transit', '2026-01-30', '2026-02-01', NULL, '2026-01-27', 0),
    
    (20, 1020, 4, 39,
     'Warehouse C - New Jersey', '357 Ashwood Cir, Detroit, MI 48201', 'FedEx', 'FDX258147369',
     'in_transit', '2026-01-31', '2026-02-02', NULL, '2026-01-28', 0),
    
    (21, 1021, 5, 41,
     'Warehouse A - California', '159 Beechwood Ln, Las Vegas, NV 89101', 'USPS', 'USPS369147258',
     'in_transit', '2026-01-30', '2026-02-01', NULL, '2026-01-27', 0),
    
    (22, 1022, 6, 43,
     'Warehouse B - Texas', '753 Elmwood Dr, Minneapolis, MN 55401', 'UPS', 'UPS951357468',
     'in_transit', '2026-02-01', '2026-02-03', NULL, '2026-01-29', 0),
    
    (23, 1023, 7, 45,
     'Warehouse C - New Jersey', '951 Pinecrest Rd, Columbus, OH 43201', 'FedEx', 'FDX357951468',
     'in_transit', '2026-01-31', '2026-02-02', NULL, '2026-01-28', 0),
    
    (24, 1024, 8, 47,
     'Warehouse A - California', '357 Maplewood Ave, Indianapolis, IN 46201', 'USPS', 'USPS852741963',
     'in_transit', '2026-02-01', '2026-02-03', NULL, '2026-01-29', 0),
    
    (25, 1025, 9, 49,
     'Warehouse B - Texas', '159 Cedarwood St, Charlotte, NC 28201', 'UPS', 'UPS741258963',
     'in_transit', '2026-01-30', '2026-02-01', NULL, '2026-01-27', 0),
    
    (26, 1026, 10, 51,
     'Warehouse C - New Jersey', '753 Birchwood Pl, San Antonio, TX 78201', 'FedEx', 'FDX654987321',
     'in_transit', '2026-02-02', '2026-02-04', NULL, '2026-01-29', 0),
    
    (27, 1027, 11, 53,
     'Warehouse A - California', '951 Willowbrook Dr, San Jose, CA 95101', 'USPS', 'USPS987321654',
     'in_transit', '2026-01-31', '2026-02-02', NULL, '2026-01-28', 0),
    
    (28, 1028, 12, 55,
     'Warehouse B - Texas', '357 Oakridge Ln, Jacksonville, FL 32201', 'UPS', 'UPS321987654',
     'in_transit', '2026-02-01', '2026-02-03', NULL, '2026-01-29', 0),
    
    -- Processing
    (29, 1029, 13, 57,
     'Warehouse C - New Jersey', '159 Maplebrook Ave, Fort Worth, TX 76101', 'FedEx', NULL,
     'processing', '2026-02-03', '2026-02-05', NULL, NULL, 0),
    
    (30, 1030, 14, 59,
     'Warehouse A - California', '753 Elmhurst St, Austin, TX 78701', 'USPS', NULL,
     'processing', '2026-02-04', '2026-02-06', NULL, NULL, 0),
    
    (31, 1031, 15, 2,
     'Warehouse B - Texas', '951 Pinebrook Rd, Seattle, WA 98101', 'UPS', NULL,
     'processing', '2026-02-03', '2026-02-05', NULL, NULL, 0),
    
    (32, 1032, 1, 4,
     'Warehouse C - New Jersey', '357 Cedarbrook Pl, Denver, CO 80201', 'FedEx', NULL,
     'processing', '2026-02-05', '2026-02-07', NULL, NULL, 0),
    
    (33, 1033, 2, 6,
     'Warehouse A - California', '159 Birchbrook Dr, Boston, MA 02101', 'USPS', NULL,
     'processing', '2026-02-04', '2026-02-06', NULL, NULL, 0),
    
    -- Exception
    (34, 1034, 3, 8,
     'Warehouse B - Texas', '753 Willowcrest Ave, Nashville, TN 37201', 'UPS', 'UPS159753486',
     'exception', '2026-01-24', '2026-01-26', NULL, '2026-01-22', 3),
    
    (35, 1035, 4, 10,
     'Warehouse C - New Jersey', '951 Oakbrook St, Memphis, TN 38101', 'FedEx', 'FDX486159753',
     'exception', '2026-01-25', '2026-01-27', NULL, '2026-01-23', 2),
    
    (36, 1036, 5, 12,
     'Warehouse A - California', '357 Maplecrest Ln, Louisville, KY 40201', 'USPS', 'USPS753486159',
     'exception', '2026-01-26', '2026-01-28', NULL, '2026-01-24', 1),
    
    (37, 1037, 6, 14,
     'Warehouse B - Texas', '159 Elmcrest Pl, Milwaukee, WI 53201', 'UPS', 'UPS486753159',
     'exception', '2026-01-27', '2026-01-29', NULL, '2026-01-25', 2),
    
    -- Cancelled
    (38, 1038, 7, 16,
     'Warehouse C - New Jersey', '753 Pinecrest Ave, Albuquerque, NM 87101', 'FedEx', 'FDX159486753',
     'cancelled', '2026-01-28', '2026-01-30', NULL, '2026-01-26', 0),
    
    (39, 1039, 8, 18,
     'Warehouse A - California', '951 Cedarhill Dr, Tucson, AZ 85701', 'USPS', NULL,
     'cancelled', '2026-02-01', '2026-02-03', NULL, NULL, 0),
    
    (40, 1040, 9, 20,
     'Warehouse B - Texas', '357 Birchhill St, Fresno, CA 93701', 'UPS', NULL,
     'cancelled', '2026-02-02', '2026-02-04', NULL, NULL, 0);


CREATE TABLE coupon_issued (
    coupon_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    delivery_id INT NOT NULL,
    coupon_code VARCHAR(50) NOT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL
);

-- Insert data into coupon_issued table
INSERT INTO public.coupon_issued (
    coupon_id, customer_id, delivery_id, coupon_code, issue_date, expiry_date
) VALUES
    (1, 1, 4, 'LATE2026-001', '2026-01-24', '2026-04-24'),
    (2, 3, 3, 'LATE2026-002', '2026-01-16', '2026-04-16'),
    (3, 2, 7, 'LATE2026-003', '2026-01-23', '2026-04-23'),
    (4, 8, 11, 'LATE2026-004', '2026-01-27', '2026-04-27'),
    (5, 12, 15, 'LATE2026-005', '2026-01-26', '2026-04-26'),
    (6, 3, 34, 'EXCEPT2026-001', '2026-01-29', '2026-04-29'),
    (7, 4, 35, 'EXCEPT2026-002', '2026-01-29', '2026-04-29'),
    (8, 5, 36, 'EXCEPT2026-003', '2026-01-29', '2026-04-29'),
    (9, 6, 37, 'EXCEPT2026-004', '2026-01-29', '2026-04-29');


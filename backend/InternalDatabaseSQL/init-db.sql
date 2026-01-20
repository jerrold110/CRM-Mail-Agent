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

INSERT INTO public.shoe_characteristics (
    product_id, product_name, size, color, material, weight, brand, price, description
)
VALUES
    (1, 'Nike Air Max', 10,  'Red',   'Leather',   0.8, 'Nike',   129.99, 'The Nike Air Max offers great cushioning and stylish design.'),
    (2, 'Nike Air Max', 9.5, 'Red',   'Leather',   0.8, 'Nike',   129.99, 'The Nike Air Max offers great cushioning and stylish design.'),
    (3, 'Adidas Ultraboost', 10,  'Black', 'Mesh',     0.7, 'Adidas', 180.00, 'The Adidas Ultraboost is known for its comfort and breathability.'),
    (4, 'Adidas Ultraboost', 9.5, 'Black', 'Mesh',     0.7, 'Adidas', 180.00, 'The Adidas Ultraboost is known for its comfort and breathability.'),
    (5, 'Puma RS-X', 10,  'Blue',  'Synthetic', 0.9, 'Puma', 110.00, 'The Puma RS-X combines bold styling with durable performance.'),
    (6, 'Puma RS-X', 9.5, 'Blue',  'Synthetic', 0.9, 'Puma', 110.00, 'The Puma RS-X combines bold styling with durable performance.'),
    (7, 'Puma RS-X', 9.5, 'Red',   'Synthetic', 0.9, 'Puma', 110.00, 'The Puma RS-X combines bold styling with durable performance.');

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
    (7, 'Puma RS-X', 75);

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

INSERT INTO public.incoming_deliveries (
    product_id, quantity, expected_date, supplier
)
VALUES
    (1, 50, '2026-01-15', 'Nike Distributor'),
    (2, 50, '2026-01-15', 'Nike Distributor'),
    (3, 30, '2026-01-20', 'Adidas Warehouse'),
    (3, 30, '2026-01-20', 'Adidas Warehouse');


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

-- Insert sample delivery data present date is january 20 2024
INSERT INTO public.item_deliveries (
    delivery_id, order_id, customer_id, product_id, 
    origin, destination, carrier, tracking_number, status,
    expected_delivery_start, expected_delivery_end, actual_delivery_date, 
    shipped_date, delivery_attempts
) VALUES
    -- On-time deliveries
    (0, 0, 0, 0,
     'Warehouse A - California', '123 Main St, New York, NY 10001', 'FedEx', 'FDX123456789',
     'delivered', '2024-01-15', '2024-01-17', '2024-01-16', '2024-01-13', 0),
    
    (1, 1, 1, 1,
     'Warehouse B - Texas', '456 Oak Ave, Seattle, WA 98101', 'UPS', 'UPS987654321',
     'delivered', '2024-01-16', '2024-01-18', '2024-01-17', '2024-01-14', 0),
    
    -- Late deliveries
    (2, 2, 2, 2,
     'Warehouse A - California', '789 Pine Rd, Austin, TX 78701', 'USPS', 'USPS456789123',
     'delivered', '2024-01-10', '2024-01-12', '2024-01-15', '2024-01-08', 2),
    
    (3, 3, 0, 3,
     'Warehouse B - Texas', '123 Main St, New York, NY 10001', 'FedEx', 'FDX111222333',
     'delivered', '2024-01-18', '2024-01-20', '2024-01-23', '2024-01-16', 1),
    
    -- In transit
    (4, 4, 3, 4,
     'Warehouse C - New Jersey', '321 Elm St, Miami, FL 33101', 'UPS', 'UPS555666777',
     'in_transit', '2024-01-20', '2024-01-22', NULL, '2024-01-18', 0),
    
    (5, 5, 4, 5,
     'Warehouse A - California', '654 Maple Dr, Portland, OR 97201', 'FedEx', 'FDX888999000',
     'in_transit', '2024-01-19', '2024-01-21', NULL, '2024-01-17', 0),
     
    -- customer 2 has a late delivery and a delivery that is currently late
    (11, 11, 2, 3,
     'Warehouse B - Texas', '123 Main St, New York, NY 10001', 'FedEx', 'FDX111222334',
     'in_transit', '2024-01-19', '2024-01-21', NULL, '2024-01-17', 0),
    
    -- Delayed in transit
    (6, 6, 2, 6,
     'Warehouse B - Texas', '789 Pine Rd, Austin, TX 78701', 'USPS', 'USPS777888999',
     'in_transit', '2024-01-17', '2024-01-19', NULL, '2024-01-15', 0),
    
    -- Out for delivery
    (7, 7, 5, 7,
     'Warehouse C - New Jersey', '159 Birch Ln, Boston, MA 02101', 'UPS', 'UPS321654987',
     'out_for_delivery', '2024-01-20', '2024-01-22', NULL, '2024-01-18', 1),
    
    -- Processing/not shipped yet
    (8, 8, 6, 8,
     'Warehouse A - California', '753 Cedar St, Denver, CO 80201', 'FedEx', NULL,
     'processing', '2024-01-23', '2024-01-25', NULL, NULL, 0),
    
    -- Exception/problem deliveries
    (9, 9, 0, 9,
     'Warehouse B - Texas', '123 Main St, New York, NY 10001', 'UPS', 'UPS147258369',
     'exception', '2024-01-14', '2024-01-16', NULL, '2024-01-12', 3),
    
    (10, 10, 7, 10,
     'Warehouse C - New Jersey', '951 Spruce Ave, Chicago, IL 60601', 'FedEx', 'FDX963852741',
     'exception', '2024-01-18', '2024-01-20', NULL, '2024-01-16', 1);
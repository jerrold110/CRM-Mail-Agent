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

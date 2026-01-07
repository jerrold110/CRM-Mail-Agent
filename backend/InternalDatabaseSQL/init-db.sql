-- Create the shoe_characteristics table
CREATE TABLE public.shoe_characteristics (
    product_id INT NOT NULL PRIMARY KEY,     -- Foreign key to the inventory table
    color VARCHAR(50),                       -- Color of the shoe (e.g., "Red", "Blue")
    material VARCHAR(50),                    -- Material of the shoe (e.g., "Leather", "Mesh")
    weight DECIMAL(5, 2),                    -- Weight of the shoe in kilograms (e.g., 0.8)
    brand VARCHAR(100),                      -- Brand name (e.g., "Nike", "Adidas")
    price DECIMAL(10, 2),                    -- Price of the product
    description TEXT                        -- Detailed description of the shoe
);

INSERT INTO public.shoe_characteristics (product_id, color, material, weight, brand, price, description)
VALUES
    (1, 'Red', 'Leather', 0.8, 'Nike', 129.99, 'The Nike Air Max offers great cushioning and stylish design.'),
    (2, 'Black', 'Mesh', 0.7, 'Adidas', 180.00, 'The Adidas Ultraboost is known for its comfort and breathability.'),
    (3, 'Blue', 'Synthetic', 0.9, 'Puma', 110.00, 'The Puma RS-X combines bold styling with durable performance.');

CREATE TABLE public.inventory (
    product_id INT NOT NULL PRIMARY KEY,
    product_name TEXT NOT NULL,             -- Name of the product (e.g., "Nike Air Max")
    size VARCHAR(10) NOT NULL,                      -- Shoe size (e.g., "10", "9.5")
    quantity INT NOT NULL     -- Stock quantity available
);

INSERT INTO public.inventory (product_id, product_name, size, quantity)
VALUES
    (1, 'Nike Air Max', '10', 100),
    (2, 'Adidas Ultraboost', '9.5', 75),
    (3, 'Puma RS-X', '8', 0);
    
CREATE TABLE public.incoming_deliveries (
    product_id INT NOT NULL,                       -- References inventory.product_id
    quantity INT NOT NULL,                         -- Quantity being delivered
    expected_date DATE NOT NULL,                   -- When delivery is expected
    received_date DATE,                            -- When delivery was actually received
    supplier VARCHAR(255),                         -- Optional supplier name
    status VARCHAR(20) NOT NULL DEFAULT 'pending'  -- pending | received | cancelled
);

INSERT INTO public.incoming_deliveries (product_id, quantity, expected_date, supplier)
VALUES
(1, 50, '2036-01-15', 'Nike Distributor'),
(2, 30, '2036-01-20', 'Adidas Warehouse'),
(3, 40, '2036-01-18', 'Puma Logistics');




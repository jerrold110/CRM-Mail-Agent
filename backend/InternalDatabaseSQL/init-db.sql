CREATE TABLE public.inventory (
    product_id SERIAL PRIMARY KEY NOT NULL,   -- Unique product identifier (auto-incremented)
    product_name VARCHAR(255) NOT NULL,  -- Name of the product (e.g., "Nike Air Max")
    size VARCHAR(10) NOT NULL,       -- Shoe size (e.g., "10", "9.5")
    quantity INT DEFAULT 0,          -- Stock quantity available
    price DECIMAL(10, 2) NOT NULL    -- Price of the product
);

INSERT INTO public.inventory (product_id, product_name, size, quantity, price)
VALUES
    (1, 'Nike Air Max', '10', 100, 129.99),
    (2, 'Adidas Ultraboost', '9.5', 75, 180.00),
    (3, 'Puma RS-X', '8', 50, 110.00);


-- Create the shoe_characteristics table
CREATE TABLE public.shoe_characteristics (
    product_id INT NOT NULL PRIMARY KEY,     -- Foreign key to the inventory table
    color VARCHAR(50),                       -- Color of the shoe (e.g., "Red", "Blue")
    material VARCHAR(50),                    -- Material of the shoe (e.g., "Leather", "Mesh")
    weight DECIMAL(5, 2),                    -- Weight of the shoe in kilograms (e.g., 0.8)
    brand VARCHAR(100),                      -- Brand name (e.g., "Nike", "Adidas")
    description TEXT,                        -- Detailed description of the shoe
    FOREIGN KEY (product_id) REFERENCES inventory (product_id)  -- Foreign key linking to the inventory table
);

-- Insert sample data into the shoe_characteristics table
INSERT INTO public.shoe_characteristics (product_id, color, material, weight, brand, description)
VALUES
    (1, 'Red', 'Leather', 0.8, 'Nike', 'The Nike Air Max offers great cushioning and stylish design.'),
    (2, 'Black', 'Mesh', 0.7, 'Adidas', 'The Adidas Ultraboost is known for its comfort and breathability.'),
    (3, 'Blue', 'Synthetic', 0.9, 'Puma', 'The Puma RS-X combines bold styling with durable performance.');


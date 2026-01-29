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

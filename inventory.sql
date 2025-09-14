select * from reorders;

select * from products;

select * from stock_entries;

select * from shipments;

select * from suppliers;

-- Total Suppliers 
select count(*) as total_suppliers from suppliers;

-- Total Products  
-- COUNT(*) returns the number of rows that exist in the table 
select count(*) as total_products from products;

-- Total Categories dealing 
select count(distinct category) as total_categories from products;

-- Total Sales cost made in last 3 months ( quantity*price ) 
select round(sum(abs(se.change_quantity)*p.price),2) as sale_last_3_months
from stock_entries as se 
join products p
on p.product_id=se.product_id
where se.change_type="Sale"
and 
se.entry_date>= 
	(
    select date_sub(max(entry_date), interval 3 month)
     from stock_entries 
     );

-- Total restock cost in last 3 months 
select round(sum(abs(se.change_quantity)*p.price),2) as restock_cost_last_3_months
from stock_entries as se 
join products p
on p.product_id=se.product_id
where se.change_type="Restock"
and 
se.entry_date>= 
	(
    select date_sub(max(entry_date), interval 3 month)
     from stock_entries 
     );

-- Products that are below restock threshold and don't have any pending/active request
select * from products as p where  p.stock_quantity < p.reorder_level
and product_id not in 
(
	select distinct product_id from reorders where status = "Pending"
);


-- Suppliers and their contact details 
select supplier_name, contact_name, email, phone from suppliers;

-- Products + their suppliers and current stock 
select p.product_name, s.supplier_name, p.stock_quantity, p.reorder_level from products as p
join 
suppliers s on 
p.supplier_id = s.supplier_id
order by p.product_name ASC;

-- Product needing reorders 
select product_id, product_name, stock_quantity, reorder_level from products where stock_quantity < reorder_level;


DELIMITER //
create procedure AddNewProductManualID(
	in p_name varchar(225),
    in p_category varchar(100),
    in p_price decimal(10,2),
    in p_stock int,
    in p_reorder int,
    in p_supplier int
    )
Begin 
	declare new_prod_id int;
    declare new_shipment_id int;
    declare new_entry_id int;
    
    # making changes in product table 
    # generate hte product id 
    select max(product_id)+1 into new_prod_id from products;
    
    insert into products(product_id, product_name, category, price, stock_quantity, reorder_level, supplier_id)
    values(new_prod_id, p_name, p_category, p_price, p_stock, p_reorder, p_supplier);
    
    # make changes in shipment table 
    select max(shipment_id)+1 into new_shipment_id from shipments;
    insert into shipments(shipment_id, product_id, supplier_id, quantity_received, shipment_date)
    values(new_shipment_id, new_prod_id, p_supplier, p_stock, curdate());
    
    
    # make changes in stock entries 
    select max(entry_id)+1 into new_entry_id from stock_entries;
    insert into stock_entries(entry_id, product_id, change_quantity, change_type, entry_date)
    values(new_entry_id, new_prod_id, p_stock, 'Restock', curdate());
    
end //
DELIMITER ;

call  AddNewProductManualID("smart watch", "Electronics", 99.99,100,25,5);
    

-- Product History
CREATE OR REPLACE view Product_Inventory_History AS 
SELECT 
pih.product_id, 
pih.action_type,
pih.record_date,
pih.Quantity,
pih.change_type,
pr.supplier_id
FROM 
(
SELECT product_id, 
"Shipment" AS action_type,
shipment_date as record_date, 
null as change_type,
quantity_received as Quantity
from shipments

UNION ALL 

SELECT product_id, 
"Stock Entry" AS action_entry,
entry_date AS record_date,
change_type as change_type,
change_quantity as Quantity
from stock_entries

)pih
join products pr on pr.product_id =pih.product_id;

-- Place order 
INSERT INTO reorders (rorder_id, product_id, reorder_quantity, reorder_date, status)
SELECT  max(reorder_id) + 1 ,100 ,200, curdate(), "Ordered" FROM reorders;


-- Receive Order 
DELIMITER //

CREATE PROCEDURE MarkReorderReceived(IN in_reorder_id INT)
BEGIN
    DECLARE product_id INT;
    DECLARE qty INT;
    DECLARE sup_id INT;
    DECLARE new_shipment_id INT;
    DECLARE new_entry_id INT;

    START TRANSACTION;

    -- Get product ID and quantity from reorders table
    SELECT product_id, reorder_quantity 
    INTO product_id, qty
    FROM reorders
    WHERE reorder_id = in_reorder_id;

    -- Get supplier ID from products table
    SELECT supplier_id 
    INTO sup_id
    FROM products 
    WHERE product_id = product_id;

    -- Mark reorder as received
    UPDATE reorders
    SET status = 'Received'
    WHERE reorder_id = in_reorder_id;

    -- Update product stock quantity
    UPDATE products 
    SET stock_quantity = stock_quantity + qty
    WHERE product_id = product_id;

    -- Insert into shipments
    SELECT MAX(shipment_id) + 1 INTO new_shipment_id
    FROM shipments;

    INSERT INTO shipments(shipment_id, product_id, supplier_id, quantity_received, shipment_date)
    VALUES (new_shipment_id, product_id, sup_id, qty, CURDATE());

    -- Insert into stock_entries
    SELECT MAX(entry_id) + 1 INTO new_entry_id 
    FROM stock_entries;

    INSERT INTO stock_entries(entry_id, product_id, change_quantity, change_type, entry_date)
    VALUES (new_entry_id, product_id, qty, 'Restock', CURDATE());

    COMMIT;
END //

DELIMITER ;


SET sql_safe_updates = 0;






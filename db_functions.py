import mysql.connector
from mysql.connector import Error


def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="MySchema"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def get_basic_info(cursor):
    queries = {
        "Total Suppliers": "SELECT COUNT(*) AS count FROM suppliers",
        "Total Products": "SELECT COUNT(*) AS count FROM products",
        "Total Product Categories ": "SELECT COUNT(DISTINCT category) AS count FROM products",
        "Total Sale Value (Last 3 Months)": """
                                            SELECT ROUND(SUM(ABS(se.change_quantity) * p.price), 2) AS total_sale
                                            FROM stock_entries se
                                                     JOIN products p ON se.product_id = p.product_id
                                            WHERE se.change_type = 'Sale'
                                              AND se.entry_date >= (SELECT DATE_SUB(MAX(entry_date), INTERVAL 3 MONTH)
                                                                    FROM stock_entries)
                                            """,
        "Total Restock Costs (Last 3 Months)": """
                                               SELECT ROUND(SUM(se.change_quantity * p.price), 2) AS total_restock
                                               FROM stock_entries se
                                                        JOIN products p ON se.product_id = p.product_id
                                               WHERE se.change_type = 'Restock'
                                                 AND
                                                   se.entry_date >= (SELECT DATE_SUB(MAX(entry_date), INTERVAL 3 MONTH)
                                                                     FROM stock_entries)
                                               """,
        "Not enough stock - Action Needed": """
                                               SELECT COUNT(*) AS below_reorder
                                               FROM products p
                                               WHERE p.stock_quantity < p.reorder_level
                                                 AND p.product_id NOT IN (SELECT DISTINCT product_id
                                                                          FROM reorders
                                                                          WHERE status = 'Pending')
                                               """
    }

    # result is a dictionary
    result = {}
    for label, query in queries.items():
        cursor.execute(query)
        row = cursor.fetchone()
        result[label] = list(row.values())[0]

    # basic info returns a dictionary
    return result

def get_additional_tables(cursor):
    queries = {
        "Suppliers Contact Details": "SELECT supplier_name, contact_name, email, phone FROM suppliers",

        "Products with Supplier and Stock": """
            SELECT 
                p.product_name,
                s.supplier_name,
                p.stock_quantity,
                p.reorder_level
            FROM products p
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            ORDER BY p.product_name ASC
        """,

        "Products Needing Reorder": """
            SELECT product_name, stock_quantity, reorder_level
            FROM products
            WHERE stock_quantity <= reorder_level
        """
    }

    tables = {}
    for label, query in queries.items():
        cursor.execute(query)
        tables[label] = cursor.fetchall()

    return tables


## Advanced queries
def add_new_manual_id(cursor, db, p_name, p_category,p_price, p_stock, p_reorder, p_supplier):
    procedure_call = "call AddNewProductManualID(%s, %s, %s, %s, %s, %s)"
    params = (p_name, p_category, p_price, p_stock, p_reorder, p_supplier)
    cursor.execute(procedure_call, params)
    db.commit()

def get_categories(cursor):
    cursor.execute("SELECT DISTINCT category FROM  products ORDER BY category ASC")
    rows = cursor.fetchall()
    return [row["category"] for row in rows]

def get_suppliers(cursor):
    cursor.execute("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name ASC")
    rows = cursor.fetchall()
    return rows

def get_all_products(cursor):
    cursor.execute("select product_id, product_name from products order by  product_name")
    return cursor.fetchall()

def get_product_history(cursor, product_id):
    query ="select * from product_inventory_history where product_id= %s order by record_date Desc"
    cursor.execute(query , (product_id,))
    return cursor.fetchall()

def place_order(cursor, db, product_id, reorder_quantity):
    query = """INSERT INTO reorders (reorder_id, product_id, reorder_quantity, reorder_date, status)
               SELECT 
                   max(reorder_id)+1,
                   %s,
                   %s,
                   curdate(),
                   "Ordered"
                FROM reorders;
            """
    cursor.execute(query, (product_id, reorder_quantity))
    db.commit()


def get_pending_reorders(cursor):
    cursor.execute("""
    SELECT * FROM reorders as r 
    JOIN products as p 
    ON r.product_id = p.product_id
    WHERE r.status = 'Pending'
    """)
    return cursor.fetchall()

def order_received(cursor, db, reorder_input):
    cursor.callproc("MarkReorderReceived", [reorder_input])
    db.commit()



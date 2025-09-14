# SQL Inventory Management System

This project is a complete inventory and supply chain management system built using Python, MySQL, and Streamlit. It provides a web-based interface for managing products, suppliers, stock levels, restocks, shipments, and reorders. The backend includes stored procedures and views to automate and track operations.

---

## Features

- Add new products and associate them with categories and suppliers
- View detailed product inventory history (including restocks and shipments)
- Place reorders for products and mark them as received
- Calculate metrics like total sales value and restock costs for the last 3 months
- View products below reorder level and pending reorders
- Streamlit-based frontend for ease of use
- MySQL stored procedures and views for backend automation

---

## Tech Stack

- **Frontend**: Streamlit (Python)
- **Backend**: Python with MySQL Connector
- **Database**: MySQL 8+

### SQL Components

- **Tables**:  
  `products`, `suppliers`, `stock_entries`, `shipments`, `reorders`

- **Views**:  
  `product_inventory_history`

- **Stored Procedures**:  
  `AddNewProductManualID`, `MarkReorderReceived`

---

## Project Structure

```
sql-inventory-app/
├── app.py                    # Streamlit frontend
├── db.py                     # MySQL connection logic
├── db_functions.py           # Database queries and stored procedure calls
├── sql/
│   ├── create_schema.sql     # Tables, views, procedures
│   └── sample_data.sql       # Optional: sample inserts
├── requirements.txt          # Python dependencies
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/titanium-exe/SQL-Inventory-Management.git
cd SQL-Inventory-Management
```

### 2. Set Up the MySQL Database

**Option A: Using MySQL Workbench**
- Open MySQL Workbench
- Run the script in `sql/create_schema.sql`

**Option B: Using Terminal**
```bash
mysql -u root -p < sql/create_schema.sql
```

If you have sample data, you can also load `sample_data.sql`.

### 3. Configure Database Connection

Edit `db.py` with your MySQL credentials:

```python
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="MySchema"
)
```

### 4. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Run the App

```bash
streamlit run app.py
```

Then open the Streamlit link in your browser.

---

## Key Stored Procedures

- **`AddNewProductManualID`**: Adds a new product and automatically inserts corresponding shipment and stock entry records.
- **`MarkReorderReceived`**: Marks a reorder as received, updates stock, adds shipment and restock entries.

---

## Example Metrics

- Total products, suppliers, and categories
- Sales and restock costs in the last 3 months
- Products needing restock without pending orders

---

## License

This project is intended for educational and demonstration purposes.


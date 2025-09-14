# SQL Inventory Management System

This project is a complete inventory and supply chain management system built using **Python**, **MySQL**, and **Streamlit**. It provides a frontend interface for managing products, suppliers, stock levels, restocks, shipments, and reorders, with support for stored procedures and views.

---

## Features

- Add new products and track them by category and supplier
- View product inventory history (restocks, shipments)
- Place reorders and receive stock with tracked entries
- Calculate inventory metrics like sales value and restock costs
- View pending orders and mark them as fulfilled
- Visual frontend built with Streamlit
- Backend logic handled with MySQL procedures and views

---

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python (with MySQL Connector)
- **Database**: MySQL 8+
- **SQL Components**:
  - Tables: `products`, `suppliers`, `stock_entries`, `shipments`, `reorders`
  - Views: `product_inventory_history`
  - Procedures: `AddNewProductManualID`, `MarkReorderReceived`

---

## Project Structure


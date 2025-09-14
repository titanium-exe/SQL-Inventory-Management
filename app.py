import pandas as pd
import streamlit as st
from db_functions import (
    get_basic_info, connect_to_db, get_additional_tables,
    get_categories, get_suppliers, add_new_manual_id, get_product_history, get_all_products, place_order,
    get_pending_reorders, order_received
)

# sidebar
st.sidebar.title("Inventory Management System")
option = st.sidebar.radio("select Options:", ["Basic Information", "Operational Tasks"])

# main space
st.title("Inventory and Supply Chain Dashboard")
db = connect_to_db()
cursor = db.cursor(dictionary=True)


# Basic Information Page
if option == "Basic Information":
    st.header("Basic Metrics")

    # get basic info from database
    # basic info is a dictionary that contain the output of all the queries
    basic_info = get_basic_info(cursor)
    cols = st.columns(3)
    # keys is a list
    keys = list(basic_info.keys())
    for i in range(3):
        cols[i].metric(label=keys[i], value=basic_info[keys[i]])
    cols = st.columns(3)
    for i in range(3,6):
        cols[i-3].metric(label=keys[i], value=basic_info[keys[i]])
    st.divider()

    # tables being displayed
    tables_dict = get_additional_tables(cursor)

    for label, table in tables_dict.items():
        st.header(label)
        pd.DataFrame(table)
        st.dataframe(table)
        st.divider()



# Operational Tasks
elif option == "Operational Tasks":
    st.header("Operational Tasks")
    operation = st.selectbox("Choose Operational Tasks", ["Add new product", "Product History", "Place Order", "Receive order"])
    if operation == "Add new product":
        st.header("Add new product")
        categories  = get_categories(cursor)
        suppliers = get_suppliers(cursor)

        with st.form("Add Product Form"):
            product_name = st.text_input("Product Name")
            product_category = st.selectbox("category", categories)
            product_price = st.number_input("Price", min_value=0.00)
            product_stock = st.number_input("Stock Quantity", min_value=1, step=1)
            product_level = st.number_input("Reorder", min_value=0, step=1)

            supplier_ids = [s["supplier_id"] for s in suppliers]
            supplier_names = [s["supplier_name"] for s in suppliers]

            supplier_id  = st.selectbox(
                "Supplier",
                options=supplier_ids,
                format_func= lambda x: supplier_names[supplier_ids.index(x)]
            )

            submitted = st.form_submit_button("Add Product")

            if submitted :
                if not product_name:
                    st.error("Please enter the product name")
                else:
                    try:
                        add_new_manual_id(cursor, db, product_name, product_category, product_price, product_stock,
                                          product_level, supplier_id)
                        st.success(f"Product {product_name} added successfully")

                    except Exception as e:
                        st.error(f"Error adding the product {e}")


    elif operation == "Product History":
        st.header("Product Inventory History")

        # get product dictionary
        products = get_all_products(cursor)
        product_names = [p['product_name'] for p in products]
        product_ids = [p["product_id"] for p in products ]

        selected_product_name = st.selectbox("Select Product", options=product_names)
        if selected_product_name:
            selected_product_id = product_ids[product_names.index(selected_product_name)]
            history_data = get_product_history(cursor, selected_product_id)

            if history_data:
                df = pd.DataFrame(history_data)
                st.dataframe(df)
            else:
                st.info("No History Found for {selected_product_name}")

    elif operation == "Place Order":
        st.header("Place the Order")
        products = get_all_products(cursor)
        product_names = [p['product_name'] for p in products]
        product_ids = [p["product_id"] for p in products]

        selected_product_name = st.selectbox("Select Product", options=product_names)

        reorder_quantity = st.number_input("Order Quantity", min_value=1, step=1)
        if st.button("Place Order"):
            if not selected_product_name:
                st.error("Please select the product")
            elif reorder_quantity <= 0:
                st.error("Reorder quantity must be greater than 0")
            else:
                selected_product_id = product_ids[product_names.index(selected_product_name)]
                try:
                    place_order(cursor, db, selected_product_id, reorder_quantity)
                    st.success(f"Order placed for {selected_product_name}")
                except Exception as e:
                    st.error(f"Error placing the order {e}")


    elif operation == "Receive order":
        st.header("Mark order as Received")

        # fetch the orders not yet received
        pending_orders = get_pending_reorders(cursor)
        if not pending_orders:
            st.info("No Pending Orders")
        else:
            reorder_ids = [r['reorder_id'] for r in pending_orders]
            reorder_labels = [f"ID {r['reorder_id']} - {r['product_name']}" for r in pending_orders]

            selected_label = st.selectbox("Select order to mark As Received", options=reorder_labels)

            if selected_label:
                selected_reorder_id = reorder_ids[reorder_labels.index(selected_label)]

                if st.button("Mark as Received"):
                    try:
                        order_received(cursor, db, selected_reorder_id)
                        st.success(f"Order ID {selected_reorder_id} marked as received")
                    except Exception as e:
                        st.error(f"Error {e}")











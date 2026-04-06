import streamlit as st
import mysql.connector
import pandas as pd



conn = mysql.connector.connect(
    host="localhost",
    user="apply_user",
    password="1234",
    database="sales_intelligence_hub"
)

cursor = conn.cursor(buffered=True)

st.set_page_config(layout="wide", page_title="Dashboard")
st.title("Dashboards Page")


with st.sidebar:
    
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")


role = st.session_state.get("role")
branch_id = st.session_state.get("branch_id")


col_1, col_2, col_3 = st.columns([1, 2, 6])

with col_1:
    st.write("Filter by Branch:")

with col_2:

    if role == "Super admin":
        
        cursor.execute("SELECT branch_name FROM branches")
        branches = ["All"] + [row[0] for row in cursor.fetchall()]

        branch_name = st.selectbox("Filter by Branch", branches, label_visibility="collapsed")

        if branch_name == "All":
            filter_condition = ""
            params = ()
        else:
            cursor.execute(
                "SELECT branch_id FROM branches WHERE branch_name = %s",
                (branch_name,)
            )
            selected_branch_id = cursor.fetchone()[0]

            filter_condition = "WHERE branch_id = %s"
            params = (selected_branch_id,)

    else:
        
        if branch_id:
            cursor.execute("""SELECT branch_name FROM branches where branch_id = %s""", (branch_id,))
            result = cursor.fetchone()[0]
            branch_list = [result]
               
        else:
            pass                
        branch_name = st.selectbox("Branch", branch_list, label_visibility = "collapsed")


        filter_condition = "WHERE branch_id = %s"
        params = (branch_id,)


col_4, col_5, col_6, col_7 = st.columns(4)

# Total Sales
with col_4:
    with st.container(border=True):
        st.write("**Total Sales**")

        cursor.execute(f"""
            SELECT SUM(gross_sales), COUNT(*)
            FROM customer_sales
            {filter_condition}
              """, params)

        total_sales, sales_count = cursor.fetchone()
        st.write(f"₹{total_sales or 0}")
        st.write(f"{sales_count} sales")

# Amount Received
with col_5:
    with st.container(border=True):
        st.write("**Amount Received**")

        cursor.execute(f"""
            SELECT SUM(received_amount),
                   COUNT(CASE WHEN received_amount > 0 THEN 1 END)
            FROM customer_sales
            {filter_condition}
        """, params)

        amount_received, amount_count = cursor.fetchone()
        st.write(f"₹{amount_received or 0}")
        st.write(f"{amount_count} transactions")

# Pending Amount
with col_6:
    with st.container(border=True):
        st.write("**Pending Amount**")

        cursor.execute(f"""
            SELECT SUM(pending_amount),
                   COUNT(CASE WHEN pending_amount > 0 THEN 1 END)
            FROM customer_sales
            {filter_condition}
        """, params)

        pending_amount, pending_count = cursor.fetchone()
        st.write(f"₹{pending_amount or 0}")
        st.write(f"{pending_count} transactions")

# Total Orders
with col_7:
    with st.container(border=True):
        st.write("**Total Orders**")

        cursor.execute(f"""
            SELECT COUNT(sale_id)
            FROM customer_sales
            {filter_condition}
        """, params)

        total_orders = cursor.fetchone()[0]
        st.write(f"{total_orders} orders")


col_8, col_9 = st.columns(2)

with col_8:
    with st.container(border=True):
        st.write("**Payment Methods**")

        query = f"""
            SELECT 
                SUM(CASE WHEN ps.payment_method = 'cash' THEN cs.received_amount ELSE 0 END),
                SUM(CASE WHEN ps.payment_method = 'UPI' THEN cs.received_amount ELSE 0 END),
                SUM(CASE WHEN ps.payment_method = 'card' THEN cs.received_amount ELSE 0 END)
            FROM customer_sales cs
            JOIN payment_splits ps ON cs.sale_id = ps.sale_id
            {filter_condition}
        """

        cursor.execute(query, params)
        cash, upi, card = cursor.fetchone()

        cash = cash or 0
        upi = upi or 0
        card = card or 0

        total_payment = cash + upi + card

        def show_payment(label, amount):
            percent = int((amount / total_payment) * 100) if total_payment > 0 else 0
            
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                st.write(label)
            with c2:
                st.progress(percent)
            with c3:
                st.write(f"₹{amount}")

        show_payment("Cash", cash)
        show_payment("UPI", upi)
        show_payment("Card", card)


with col_9:
    with st.container(border=True):
        st.write("**Sales Status**")

        cursor.execute(f"""
            SELECT 
                COUNT(CASE WHEN status = 'open' THEN 1 END),
                COUNT(CASE WHEN status = 'close' THEN 1 END)
            FROM customer_sales
            {filter_condition}
        """, params)

        open_count, close_count = cursor.fetchone()

        c1, c2 = st.columns(2)

        with c1:
            with st.container(border=True):
                st.write(open_count)
                st.write("Open")

        with c2:
            with st.container(border=True):
                st.write(close_count)
                st.write("Close")

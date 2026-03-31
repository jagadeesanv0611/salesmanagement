import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date as dt_date



conn = mysql.connector.connect(
    host="localhost",
    user="apply_user",
    password="1234",
    database="sales_intelligence_hub"
)

st.set_page_config(layout="wide", page_title="Pending Payments")
st.title("Pending Payments Page")


with st.sidebar:
    
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")


role = st.session_state.get("role")
branch_id = st.session_state.get("branch_id")

cursor = conn.cursor()


if role == "Admin":
    condition = "AND branch_id = %s"
    params = (branch_id,)
else:
    condition = ""
    params = ()


coln_1, coln_2, coln_3 = st.columns(3)



with coln_1:
    with st.container(border=True):
        st.write("**TOTAL PENDING**")

        cursor.execute(f"""
            SELECT SUM(pending_amount), COUNT(*)
            FROM customer_sales
            WHERE status='open' {condition}
        """, params)

        total_pending, total_count = cursor.fetchone()
        st.write(f"₹{total_pending or 0}")
        st.write(f"{total_count} transactions")




with coln_2:
    with st.container(border=True):
        st.write("**OVERDUE**")

        cursor.execute(f"""
            SELECT SUM(pending_amount), COUNT(*)
            FROM customer_sales
            WHERE date < CURDATE() AND status='open' {condition}
        """, params)

        overdue_amt, overdue_count = cursor.fetchone()
        st.write(f"₹{overdue_amt or 0}")
        st.write(f"{overdue_count} transactions")

with coln_3:
    with st.container(border=True):
        st.write("**DUE THIS WEEK**")

        cursor.execute(f"""
            SELECT SUM(pending_amount), COUNT(*)
            FROM customer_sales
            WHERE status='open'
            AND date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            {condition}
        """, params)

        due_amt, due_count = cursor.fetchone()
        st.write(f"₹{due_amt or 0}")
        st.write(f"{due_count} transactions")

with st.container(border=True, height=400):
    st.write("**Pending Payment List**")

    if branch_id is not None:
        cursor.execute("""
            SELECT cs.sale_id, cs.name, b.branch_name, cs.date, cs.pending_amount
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
            WHERE cs.status='open' AND cs.branch_id = %s
        """, (branch_id,))
    else:
        cursor.execute("""
            SELECT cs.sale_id, cs.name, b.branch_name, cs.date, cs.pending_amount
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
            WHERE cs.status='open'
        """)

    rows = cursor.fetchall()

    for row in rows:
        sale_id, name, branch_name, sale_date, pending_amount = row

        overdue_days = (dt_date.today() - sale_date).days

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.write(f"**{name}** - sale id = {sale_id}")
            if overdue_days > 0:
                st.write(f"{branch_name} , {sale_date} ,  {overdue_days} days overdue")                
            else:
                st.write(f"{branch_name} , {sale_date} ,  {abs(overdue_days)} days left")         

        with col3:
            st.write(f"₹{pending_amount}")

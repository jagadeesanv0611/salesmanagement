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
st.title("Analytics")

role = st.session_state.get("role")
branch_id = st.session_state.get("branch_id")


with st.sidebar:
     
     if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")
     

col_1, col_2, col_3 = st.columns([1,1,1])

with col_1:
    with st.container(border=True):
        st.write("**Avg Sale Value**")
        cursor = conn.cursor()
        if role == "Super admin":
            cursor.execute("SELECT AVG(gross_sales) FROM customer_sales")
        else:
            cursor.execute("SELECT AVG(gross_sales) FROM customer_sales WHERE branch_id=%s", (branch_id,))
        avg_sale_value = cursor.fetchone()[0] or 0

        avg_sale = round(avg_sale_value,2)
        st.write(f"**₹{avg_sale}**")


with col_2: 
    with st.container(border=True): 
        st.write("**Collection Rate**") 
        cursor = conn.cursor() 
        if role == "Super admin": 
         cursor.execute("SELECT SUM(received_amount) FROM customer_sales") 

        else: 
         cursor.execute(""" SELECT SUM(received_amount) FROM customer_sales WHERE branch_id=%s """, (branch_id,)) 
        total_received_amount = cursor.fetchone()[0] 

        cursor = conn.cursor() 
        if role == "Super admin": 
         cursor.execute("SELECT SUM(gross_sales) FROM customer_sales") 

        else: 
         cursor.execute(""" SELECT SUM(gross_sales) FROM customer_sales WHERE branch_id=%s """, (branch_id,))
        total_gross_sales = cursor.fetchone()[0] 
        collection_rate = round(((total_received_amount / total_gross_sales) * 100),2) 
        st.write(f"**{collection_rate} %**")



with col_3:
    with st.container(border=True):
        st.write("**Top Branch**")
        cursor = conn.cursor()
        if role == "Super admin":
            cursor.execute("""
                SELECT SUM(cs.gross_sales), b.branch_name
                FROM customer_sales cs
                JOIN branches b ON cs.branch_id = b.branch_id
                GROUP BY b.branch_name
                ORDER BY SUM(cs.gross_sales) DESC
                LIMIT 1
            """)
            
        else:
            cursor.execute("""
                SELECT SUM(cs.gross_sales), b.branch_name
                FROM customer_sales cs
                JOIN branches b ON cs.branch_id = b.branch_id
                WHERE cs.branch_id=%s
                GROUP BY b.branch_name
            """, (branch_id,))

        result = cursor.fetchone()
        high_val = result[0] or 0
        top_branch = result[1]
        st.write(f"**₹{high_val} - {top_branch}**")

with st.container(border=True, height = 400):
        st.write("**Branch Performance**")
        
        cursor = conn.cursor()

        if role == "Super admin":
            cursor.execute("""
            SELECT b.branch_name,
                   SUM(cs.received_amount),
                   SUM(cs.gross_sales)
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
            GROUP BY b.branch_name
             ORDER BY SUM(cs.received_amount) DESC
                  """)
        
        else:
            cursor.execute("""
            SELECT b.branch_name,
                   SUM(cs.received_amount),
                   SUM(cs.gross_sales)
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
            WHERE cs.branch_id=%s
            GROUP BY b.branch_name
           """, (branch_id,))
        
        rows = cursor.fetchall()

        for row in rows:
           branch_name = row[0]
           total_received_amount = row[1] or 0
           total_gross_sales = row[2] or 0

           if total_gross_sales > 0:
              percent = int(((total_received_amount / total_gross_sales) * 100))
           else:            
               0


           col_4, col_5, col_6, col_7 = st.columns([1,1,1,1])

           with col_4:
                st.write(f"**{branch_name}**")              
         
           with col_5:
                st.progress(percent)

           with col_6:
                st.write(f"**₹{total_received_amount}**")
        
           with col_7:
                st.write(f"**{percent}% collected**")
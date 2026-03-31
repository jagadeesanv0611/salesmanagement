import streamlit as st
import mysql.connector
import pandas as pd


conn = mysql.connector.connect(
    host="localhost",
    user="apply_user",
    password="1234",
    database="sales_intelligence_hub"
)

st.set_page_config(layout="wide", page_title="Payment Splits")
st.title("Payment Splits Page")



with st.sidebar:
    
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")


role = st.session_state.get("role")
branch_id = st.session_state.get("branch_id")


if "show_new_payment_split" not in st.session_state:
    st.session_state.show_new_payment_split = False


col_btn1, col_btn2, col_btn3 = st.columns([2,1,6])

with col_btn1:
    if st.button(":blue[**+ Add New Payment Splits**]"):
        st.session_state.show_new_payment_split = True



def Add_new_payment_split_button():

    cursor = conn.cursor(buffered=True)

    
    if role == "Admin":
        cursor.execute(
            "SELECT sale_id FROM customer_sales WHERE branch_id = %s",
            (branch_id,)
        )
    else:
        cursor.execute("SELECT sale_id FROM customer_sales")

    sale_ids = [row[0] for row in cursor.fetchall()]

    with st.form("payment_form"):
        st.write("* Add Payment Split *")

        col_1, col_2 = st.columns(2)
        with col_1:
            sale_id = st.selectbox('Sale ID', sale_ids)
        with col_2:
            payment_date = st.date_input('Date')

        col_3, col_4 = st.columns(2)
        with col_3:
            amount_paid = st.number_input("Amount Received (₹)", min_value=0.0)
        with col_4:
            payment_method = st.selectbox("Payment Method", ("cash", "UPI", "card"))

        save_sale = st.form_submit_button("Save")
        cancel_sale = st.form_submit_button("Cancel")

        if save_sale:
            
            cursor = conn.cursor()

            cursor.execute("""
                    INSERT INTO payment_splits 
                    (sale_id, payment_date, amount_paid, payment_method)
                    VALUES (%s, %s, %s, %s)
                """, (sale_id, payment_date.isoformat(), amount_paid, payment_method))

            conn.commit()

            st.success("Payment added successfully ")

            st.session_state.show_new_payment_split = False

           

        elif cancel_sale:
            st.warning("Cancelled")
            st.session_state.show_new_payment_split = False


if st.session_state.show_new_payment_split:
    Add_new_payment_split_button()

st.write("Payment Split Records")

cursor = conn.cursor(buffered=True)

if role == "Admin":
    cursor.execute("""
        SELECT ps.* 
        FROM payment_splits ps
        JOIN customer_sales cs ON ps.sale_id = cs.sale_id
        WHERE cs.branch_id = %s
    """, (branch_id,))
else:
    cursor.execute("SELECT * FROM payment_splits")

rows = cursor.fetchall()
columns = [col[0] for col in cursor.description]

df = pd.DataFrame(rows, columns=columns)
st.dataframe(df)

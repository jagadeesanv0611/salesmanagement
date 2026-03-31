import streamlit as st
import mysql.connector
import pandas as pd



conn = mysql.connector.connect(
    host="localhost",
    user="apply_user",
    password="1234",
    database="sales_intelligence_hub"
)

st.set_page_config(layout="wide", page_title="Sales Record")
st.title("**Sales Record**")

with st.sidebar:
     
     if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")



if "show_new_sale_form" not in st.session_state:
    st.session_state.show_new_sale_form = False


col_btn1, col_btn2, col_btn3 = st.columns([1,1,6])


with col_btn1:
    if st.button(":blue[*+ New Sale*]"):
        st.session_state.show_new_sale_form = True



def Add_new_sale_button():

    branch_id = st.session_state.get("branch_id")

    with st.form("my_form"):
        st.write("*+ Add New Sale*")

        col1, col2 = st.columns(2)
        with col1:
            cursor = conn.cursor(buffered=True)
            if branch_id:
               cursor.execute("""SELECT branch_name FROM branches where branch_id = %s""", (branch_id,))
               result = cursor.fetchone()[0]
               branch_list = [result]
               
            else:
                cursor.execute("SELECT branch_name FROM branches")
                result = cursor.fetchall()
                branch_list = [row[0] for row in result]
                
            branch_name = st.selectbox("Branch", branch_list)

        with col2:
            date = st.date_input('Date')


        col3, col4 = st.columns(2)
        with col3:
            customer_name = st.text_input('Customer Name')
        with col4:
            mobile_number = st.text_input('Mobile Number')

        product_name = st.text_input('Product Name')

        col_5, col_6 = st.columns(2)
        with col_5:
            gross_sales = st.number_input("Total Amount (₹)", min_value=0.00)
        with col_6:
            status = st.selectbox("Status", ("open", "close"))


        save_sale = st.form_submit_button("Save")
        cancel_sale = st.form_submit_button("Cancel")


        if save_sale:
            
            cursor = conn.cursor(buffered=True)                
            cursor.execute("SELECT branch_id FROM branches WHERE branch_name = %s", (branch_name,))
            branch_id = cursor.fetchone()[0]

                
            cursor.execute(
                    """INSERT INTO customer_sales (branch_id, date, name, mobile_number, product_name,
                    gross_sales, status) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (branch_id, date.isoformat(), customer_name, mobile_number, product_name, gross_sales, status)
                )
            conn.commit()

            st.success(f"Sale saved successfully! ({cursor.rowcount} record inserted)")

                
            cursor.execute("SELECT COUNT(*) FROM customer_sales")
            st.write("Total rows in customer_sales:", cursor.fetchone()[0])

            st.session_state.show_new_sale_form = False            

        elif cancel_sale:
            st.warning("Sale cancelled.")
            st.session_state.show_new_sale_form = False


if st.session_state.show_new_sale_form:
  Add_new_sale_button()


st.markdown("*All Sales Records*")
branch_id = st.session_state.get("branch_id")


if branch_id:
    cursor = conn.cursor(buffered=True)
    cursor.execute("SELECT * FROM customer_sales where branch_id = %s", (branch_id,))
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df)
else:
    cursor = conn.cursor(buffered=True)
    cursor.execute("SELECT * FROM customer_sales")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df)








# conn.close()
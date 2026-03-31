import streamlit as st
import mysql.connector
import pandas as pd


conn = mysql.connector.connect(
    host="localhost",
    user="apply_user",                   
    password="1234",                     
    database="Sales_Intelligence_Hub"
)

cursor = conn.cursor()

st.set_page_config(page_title='Login Page')
st.title("**Login page**")



user_name = st.text_input('username')
user_password = st.text_input('user_password', type='password') 


if st.button('sign in'):
    access = 'select * from users where username=%s AND user_password=%s'
    cursor.execute(access, (user_name, user_password))
    result = cursor.fetchone()

    if result:
        branch_id = result[3]
        role = result[4]

       
        st.session_state['branch_id'] = branch_id
        st.session_state['role'] = role
        
        st.success('Sign in successful')
        st.switch_page("pages/02_sales_record.py")
        
        
    else:
        st.error('invalid user_name or password')
 
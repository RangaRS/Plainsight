import streamlit as st
from database import fetch_table_data


@st.cache_data
def get_customer_list():
    query = f'select customer_name, count(customer_name) as total_tickets from tickets group by customer_name;'
    customerList = fetch_table_data(query).collect()
    return customerList
    

def render_customer_list():
    
    columns = 3
    customerList = get_customer_list()
    cols = st.columns(columns)

    for i,customer in enumerate(customerList):
        url = f"/customers?orgname={customer['CUSTOMER_NAME']}"
        
        with cols[i%columns]:
            with st.container(border=True):
                st.subheader(customer['CUSTOMER_NAME'])
                st.write('Total Tickets: ' + str(customer['TOTAL_TICKETS']))
                st.html(f'<a href="{url}">Visit page -></a>')
            

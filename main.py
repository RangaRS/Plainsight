import streamlit as st
from Utils.utils import loadCSS
st.set_page_config(layout="wide", menu_items=None)
st.markdown(loadCSS('main.css'), unsafe_allow_html=True)

from database import fetch_table_data
import Module.Customers.customerlist as cl
import Module.Customers.customerDetails as cd
from Module.Tags.tags import render_all_tags, render_tag_page
from Module.chat import render_chat
from Module.home import render_homepage
import Module.Tickets.tickets as ts


def homepage():
    empty1, main, empty2 = st.columns([0.02,0.96,0.02])
    with main:
        # st.progress(80, 'Sample progress')
        # st.title("This is the homepage 🏠")
        all_tickets = fetch_table_data('select * from tickets').to_pandas()
        render_homepage(all_tickets)
    

def customers():
    if 'orgname' in st.query_params:
        orgname = st.query_params['orgname']
        gap1, main, gap2, chat = st.columns([0.02,0.68,0.01,0.3])
        
        with main:
            st.html("<div style='width:20px'></div>")
            cd.render_customer_details(orgname)
            st.html("<div style='width:20px'></div>")
        
        with chat:
            filters = {'@eq':{'customer_name': orgname}}
            st.subheader(f"Ask bot about {orgname}")
            # st.caption(f"Ask bot about {orgname}")
            render_chat(filters=filters)

    else:
        cl.render_customer_list()  
        

def tickets():
    main, chat = st.columns([0.999, 0.001])
    if 'ticketid' in st.query_params:
        ticketid = st.query_params['ticketid']
        
        with main:
            ts.render_ticket_page(ticketid)
        
    else:
        with main:
            ts.render_all_tickets('*')
            

def tags():
    
    e1, main, e2 = st.columns([0.02,0.96,0.02])
    
    with main:
        if 'name' in st.query_params:
            render_tag_page(st.query_params['name'])
        else:
            render_all_tags()


def  chatbot():
    
    e1, main, e2 = st.columns([0.02,0.96,0.02])
    with main:
        render_chat()
    
    
    
    
st.logo('./assets/logo.png', size='large')           
# st.logo('./assets/logo_full.png', size='large')   
pg = st.navigation([
    st.Page(homepage, title="Homepage", icon="🔥"),
    st.Page(customers, title="Customers", icon="🏢"),
    st.Page(tickets, title="Tickets", icon="🎫"),
    st.Page(tags, title="Tags", icon="#️⃣"),
    st.Page(chatbot, title="Chatbot", icon="💬"),
])
pg.run()


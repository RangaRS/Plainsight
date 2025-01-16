import streamlit as st
import Utils.components as components
from database import session, fetch_table_data, perform_analyst_search, perform_search_service, ai_summarize

@st.cache_data
def fetch_all_tickets(org):
    
    if org == '*':
        return fetch_table_data(f"select * from tickets").to_pandas()
    else:
        return fetch_table_data(f"select * from tickets where customer_name='{org}'").to_pandas()



def render_all_tickets(orgname):
    st.session_state.all_tickets = fetch_all_tickets(orgname)
    for i,ticket in st.session_state.all_tickets.iterrows():
        st.html(components.ticket_card(ticket))


@st.cache_data
def fetch_ticket_data(id):
    return fetch_table_data(f"select * from tickets where id={id}").to_pandas()


@st.cache_data
def fetch_ticket_tags_data(id):
    return fetch_table_data(f"select * from tag where ticket_id={id}").to_pandas()


@st.cache_data
def fetch_similar_tickets(tags):
    
    conditions = ''
    for i,t in tags.iterrows():
        conditions += f"""(type='{t.TYPE}' and name='{t.NAME}')"""
        if i < tags['ID'].count() - 1 :
            conditions += ' or '
    
    query = f"""
        select * from tickets where id in 
        (select 
            distinct ticket_id
            from 
                tag
            where
                {conditions})
    
    """
    # st.code(query, language='sql')
    return fetch_table_data(query).to_pandas()




def render_ticket_page(id):
    
    comments_tab, overview_tab, similar_tickets_tab = st.tabs(['Comments', 'Overview', 'Similar Tickets'])
    
    ticket_details = fetch_ticket_data(id)
    tag_details = fetch_ticket_tags_data(id)
    similar_tickets = fetch_similar_tickets(tag_details)

    
    for i,ticket in ticket_details.iterrows():
        st.html(components.ticket_title_card(ticket))
        
    with overview_tab:
        st.table(ticket)
    
    with similar_tickets_tab:
        for i,t in similar_tickets.iterrows():
            st.html(components.ticket_card(t))

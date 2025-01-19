import streamlit as st
import Utils.components as components
import pandas as pd
from database import session, fetch_table_data, perform_analyst_search, perform_search_service, ai_summarize

@st.cache_data
def fetch_all_tickets(org):
    
    if org == '*':
        return fetch_table_data(f"select * from tickets").to_pandas()
    else:
        return fetch_table_data(f"select * from tickets where customer_name='{org}'").to_pandas()



def render_all_tickets(orgname):
    st.session_state.all_tickets = fetch_all_tickets(orgname)
    
    empty1, main_col, empty2 = st.columns([0.02, 0.96,0.02]) 
    
    with main_col:
        ticketSearch = st.text_input('Search for tickets...', key='ticket_search')
        tickets_container = st.container()
        for i,ticket in st.session_state.all_tickets.iterrows():
            tickets_container.container().html(components.ticket_card(ticket))
    
    if ticketSearch:
        search_tickets = perform_search_service(st.session_state.ticket_search, limit=10)
        tickets = search_tickets['results']
        tickets = pd.DataFrame(tickets)
        
        with tickets_container:
            for i,ticket in tickets.iterrows():
                st.container().html(components.ticket_card(ticket))


@st.cache_data
def fetch_ticket_data(id):
    return fetch_table_data(f"select * from tickets where id={id}").to_pandas()


@st.cache_data
def fetch_ticket_tags_data(id):
    return fetch_table_data(f"select * from tag where ticket_id={id}").to_pandas()


@st.cache_data
def fetch_comments_data(id):
    return fetch_table_data(f"select * from comments where ticket_id={id}").to_pandas()


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
    
    empty1, main_col, empty2, details_col = st.columns([0.02, 0.66,0.02, 0.3]) 
    
    ticket_details = fetch_ticket_data(id)
    comments = fetch_comments_data(id)
    tag_details = fetch_ticket_tags_data(id)
    tags = tag_details.groupby(by='TYPE')['NAME']
    similar_tickets = fetch_similar_tickets(tag_details)
    # st.table(tag_details)
    # st.table(tags)
    
    with main_col:
        for i,ticket in ticket_details.iterrows():
            st.html(components.ticket_title_card(ticket, tags))

            
            
        resolved_comment_container = st.container()            
                
        comments_tab, similar_tickets_tab = st.tabs(['Comments', 'Similar Tickets'])
                    
        with comments_tab:
            
            for i,t in comments.iterrows():
                # with st.chat_message(name='user'):
                st.html(components.comment_card(t))
                if t.IS_RESOLVED:
                    resolved_comment_container.expander('Accepted Solution').html(components.comment_card(t))    
        
        with similar_tickets_tab:
            for i,t in similar_tickets.iterrows():
                st.html(components.ticket_card(t))
    
    with details_col:
        ticket = ticket.drop(['PROJECT_LEAD_ID', 'ISSUE_KEY', 'ISSUE_ID', 'PROJECT_KEY', 'PROJECT_NAME', 'PROJECT_TYPE', 'PROJECT_LEAD_ID', 'ASSIGNEE_ID', 'REPORTER_ID', 'CREATOR_ID', 'DESCRIPTION', 'SUMMARY', 'AI_SUMMARY', 'WATCHERS_ID', 'ENVIRONMENT', 'PARENT', 'PARENT_SUMMARY', 'STATUS_CATEGORY', 'STATUS_CATEGORY_CHANGED'])
        columns = ticket.keys()
        container = st.container(border=True)
        container.subheader("Ticket Details")
        for k in columns:
            # print(columns)
            container.html(components.table_cell(k, ticket[k]))
            # st.write(f"{k} : {ticket[k]}")

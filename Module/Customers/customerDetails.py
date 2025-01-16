import streamlit as st
from Utils.components import ticket_card, customer_title_card
from database import session, fetch_table_data, perform_analyst_search, perform_search_service, ai_summarize

st.session_state.all_tickets = ''

@st.cache_data
def fetch_all_tickets(org):
    print(org, "running now \n ----------------------------------------------------------")
    return fetch_table_data(f"select * from tickets where customer_name = '{org}'").to_pandas()


# @st.cache_data
# def summarize_tickets(orgname):
#     org = orgname
#     # tickets = fetch_all_tickets(orgname)
#     summary = st.session_state.all_tickets.get(['CUSTOMER_NAME','SUMMARY','DESCRIPTION','CREATED','ISSUE_TYPE','STATUS','SENTIMENT'])
#     ai_summary = []
    
#     for i,row in summary.iterrows():
#         ticket_detail = f"CUSTOMER_NAME: {row['CUSTOMER_NAME']}, TICKET CREATED ON: {row['CREATED']}, SUMMARY: {row['SUMMARY']}, DESCRIPTION: {row['DESCRIPTION']}, ISSUE TYPE: {row['ISSUE_TYPE']}, TICKET STATUS: {row['STATUS']}, SENTIMENT OF THE USER: {row['SENTIMENT']}"
#         ticket_detail = ticket_detail.replace("'","")
        
#         query = f"select snowflake.cortex.SUMMARIZE('For the given customer support ticket information. generate a summary with crisp and key information in a well structured manner. TICKETS SUMMARY: {ticket_detail}.')"
#         ai_response = session.sql(query).collect()
#         ai_summary.append(ai_response[0][0])
    
#     return ai_summary


@st.cache_data
def summarize_tickets(orgname):
    org = orgname
    # tickets = fetch_all_tickets(orgname)
    summary = st.session_state.all_tickets.get(['ID','AI_SUMMARY','CREATED','ISSUE_TYPE','STATUS','SENTIMENT'])
    ai_summary = []
    
    for i,row in summary.iterrows():
        ticket_detail = f"TICKET_ID: {row['ID']}, \nAI_SUMMARY: {row['AI_SUMMARY']}, \nTICKET CREATED ON: {row['CREATED']}, \nISSUE TYPE: {row['ISSUE_TYPE']}, \nTICKET STATUS: {row['STATUS']}, \nSENTIMENT OF THE USER: {row['SENTIMENT']}"
        ticket_detail = ticket_detail.replace("'","")
        
        ai_summary.append(ticket_detail)
    
    return ai_summary


@st.cache_data
def generate_summary(text):
        text = str(text).replace("'","")
        overall_query = f"""select snowflake.cortex.complete('mistral-large2','You are an expert analyst specializing in identifying issues and opportunities for SaaS companies.
                                                            Given the provided customer support ticket information provide a summary in paragraphs for:
                                                            - Customer Overview, including the overall sentiment and consolidated summary based on all the tickets combined as a single paragraph.
                                                            - Product usage pattern.
                                                            - Key features and issue types.
                                                            - Include Metrics and Analytics.
                                                            DO NOT TALK ABOUT INDIVIDUAL TICKETS. ONLY PROVIDE GENERAL SUMMARY OF EVERYTHING COMBINED.
                                                            Input:
                                                            Ticket Details: {text}
                                                            Provide the whole response in not more than 250 words;
                                                            Response Format: Present your response in a well structured manner with right lines, spaces, and indentations. if possible in a markdown format.
                                                            ')"""
                                                            
        overall_ai_response = session.sql(overall_query).collect()
        
        return overall_ai_response[0][0]
        

def render_customer_details(orgname):
    st.session_state.all_tickets = fetch_all_tickets(orgname)

    st.html(customer_title_card(orgname, 'Happy', 'For 45 days'))

    general, tickets, notes = st.tabs(['General Summary', 'All Tickets', 'Private Notes'])

    with general:
        with st.expander(f'About {orgname}'):
            ticks_summary = summarize_tickets(orgname)
            overall_summary = generate_summary(ticks_summary)
            
            st.markdown(overall_summary) 
        st.divider()
        
        senti_vs_status = st.session_state.all_tickets.get(['SENTIMENT','STATUS']).value_counts().reset_index()
        st.subheader('Sentiment VS Status')
        st.bar_chart(senti_vs_status, x='SENTIMENT', y='count', color='STATUS', horizontal=True)  
        st.divider()
        
        priority_vs_status = st.session_state.all_tickets.get(['PRIORITY','STATUS']).value_counts().reset_index()
        st.subheader('Priority VS Status')
        st.scatter_chart(priority_vs_status, y='PRIORITY', x='STATUS', size='count')  
        st.divider()
        
        
        
    with tickets:
        for i,ticket in st.session_state.all_tickets.iterrows():
            st.html(ticket_card(ticket))
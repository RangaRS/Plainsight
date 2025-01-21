import numpy as np
import streamlit as st
import Utils.components as components
import pandas as pd
from database import askAI, session, fetch_table_data, perform_search_service
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
import markdown

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
        empty_container = st.empty()
        html =''

        if ticketSearch:
            search_tickets = perform_search_service(st.session_state.ticket_search, limit=10)
            tickets = search_tickets['results']
            tickets = pd.DataFrame(tickets)
            empty_container.empty()
  
        else:
            tickets = st.session_state.all_tickets
          
          
        for i,ticket in tickets.iterrows():
            html += components.ticket_card(ticket)
            html += '<br>'
        
        empty_container.html(html)


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
def fetch_similar_tickets(ids):
    query = f"""select * from tickets where id in ({ids})"""
    return fetch_table_data(query).to_pandas()


@st.cache_data
def fetch_solution_from_tickets(source_ticket_summary):
    
    input_question = source_ticket_summary.replace("'", "")
    vector_sql = "SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('SNOWFLAKE-ARCTIC-EMBED-M-V1.5','" + input_question +"');"
    q_vector = session.sql(vector_sql).collect()
    qv = []
    for v in q_vector[0]:
        qv = np.array(v).reshape(1,-1)
    
    cortex_results = perform_search_service(input_question, limit=50)
    cortex_tickets = cortex_results['results']
    cortex_tickets = pd.DataFrame(cortex_tickets)
    
    ids = ''
    for id in cortex_tickets['ID']:
        ids += str(id) + ','
    
    ids = ids[:-1]
    data = session.sql(f'SELECT id,description, "_GENERATED_EMBEDDINGS_SNOWFLAKE-ARCTIC-EMBED-M-V1.5" as embedding FROM TABLE ( CORTEX_SEARCH_DATA_SCAN ( SERVICE_NAME => \'SEARCH_TICKET_SUMMARY_DESCRIPTION\' )) where id in ({ids});').collect()

    matching_data = []
    matching_ids = ''
    dataList = enumerate(data)
    for i,d in dataList:
        cv = data[i]["EMBEDDING"]
        cv = np.array(cv).reshape(1,-1)
        similarity = cosine_similarity(qv, cv)
        distances = cosine_distances(qv, cv)
        
        if (similarity > 0.6):
            matching_data.append(data[i]['ID'])
            if(matching_ids == ''):
                matching_ids += str(data[i]['ID'])
            else:
                matching_ids = matching_ids + ',' + str(data[i]['ID'])
                
    data = session.sql("select COMMENT from comments where ticket_id in (" + matching_ids +") and is_resolved = TRUE;").to_pandas()
    dataList = data.iterrows()
    
    comments = ''
    
    for i,d in dataList:
        cv = d["COMMENT"]
        answer = i+1
        if(comments == ''):
            comments += str(answer) + '. ' + cv
        else:
            comments = comments + '\n' + str(answer) + '. ' + cv
    
    return {'comments':comments, 'ticket_ids': matching_ids}


@st.cache_data
def generate_suggestions(get_ans_query):
    return askAI(get_ans_query)


def render_ticket_page(id):
    
    empty1, main_col, empty2, details_col = st.columns([0.02, 0.66,0.02, 0.3]) 
    
    ticket_details = fetch_ticket_data(id)
    ticket = ticket_details.iterrows()
    ticket = ''
    
    for i,ticket in ticket_details.iterrows():
        ticket = ticket
        
    comments = fetch_comments_data(id)
    tag_details = fetch_ticket_tags_data(id)
    tags = tag_details.groupby(by='TYPE')['NAME']
    resolved_tickets = fetch_solution_from_tickets(ticket['DESCRIPTION'])
    
    similar_ticket = fetch_similar_tickets(resolved_tickets['ticket_ids'])
    similar_ticket = similar_ticket.sort_values('RESOLUTION')
    
    get_ans_query = f""" You are an helpful assistant who is skilled at extracting answers from a bunch of points for a given user query.
                        I have attached the user query and the already existing possible solutions.
                        Please analyse, extract, summarize and provide a solution for the asked question.
                        \n\n\n
                        USER QUESTION: {ticket['DESCRIPTION'].replace("'", "")}
                        \n\n\n
                        SUGGESTED POTENTIAL ANSWERS: {str(resolved_tickets['comments']).replace("'", '')}
                        \n\n\n
                        WRITE THE ANSWER IN A STEP-BY-STEP SOLUTION HELPING USERS TO FOLLOW WITH AND RESOLVE THEIR ISSUE.
                        SUMMARIZE THE SOLUTION ONLY FROM THE GIVEN SUGGESTED ANSWERS. IF NOTHING RELEVANT IS AVAILABLE, RESPOND SAYING "There are no relevant answers available." 
                        DONT TRY TO ACT SMART.
                        LIMIT THE SOLUTION TO 100 WORDS
                     """
    get_ans = askAI(get_ans_query)

    
    with main_col:
        for i,ticket in ticket_details.iterrows():
            st.html(components.ticket_title_card(ticket, tags))
 
        resolved_comment_container = st.container()            
                
        comments_tab, similar_tickets_tab = st.tabs(['Comments', 'Similar Tickets'])
                    
        with comments_tab:     
            for i,t in comments.iterrows():
                st.html(components.comment_card(t))
            
                if t.IS_RESOLVED:
                    resolved_comment_container.expander('Accepted Solution').html(components.comment_card(t))    
        
        with similar_tickets_tab:
            resolved_comment_container.html(components.ai_summary(markdown.markdown(get_ans)))

            for i,t in similar_ticket.iterrows():
                st.html(components.ticket_card(t))
    
    with details_col:
        ticket = ticket.drop(['PROJECT_LEAD_ID', 'ISSUE_KEY', 'ISSUE_ID', 'PROJECT_KEY', 'PROJECT_NAME', 'PROJECT_TYPE', 'PROJECT_LEAD_ID', 'ASSIGNEE_ID', 'REPORTER_ID', 'CREATOR_ID', 'DESCRIPTION', 'SUMMARY', 'AI_SUMMARY', 'WATCHERS_ID', 'ENVIRONMENT', 'PARENT', 'PARENT_SUMMARY', 'STATUS_CATEGORY', 'STATUS_CATEGORY_CHANGED'])
        columns = ticket.keys()
        container = st.container(border=True)
        container.subheader("Ticket Details")

        for k in columns:
            container.html(components.table_cell(k, ticket[k]))

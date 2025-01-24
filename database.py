import requests
from snowflake.snowpark import Session
import streamlit as st

connection_parameters = {
  "account" : st.secrets["SNOWFLAKE"]["SNOWFLAKE_ACCOUNT_LOCATOR"],
   "user" : st.secrets["SNOWFLAKE"]["SNOWFLAKE_USER"],
   "password" : st.secrets["SNOWFLAKE"]["SNOWFLAKE_PASSWORD"],
   "role": st.secrets["SNOWFLAKE"]["SNOWFLAKE_ROLE"],
   "warehouse":st.secrets["SNOWFLAKE"]["SNOWFLAKE_WAREHOUSE"],
   "database":st.secrets["SNOWFLAKE"]["SNOWFLAKE_DATABASE"],
   "schema":st.secrets["SNOWFLAKE"]["SNOWFLAKE_SCHEMA"]
}

# Connection Params:
HOST = st.secrets["SNOWFLAKE"]["SNOWFLAKE_HOST"]
ACCOUNT = connection_parameters['account']
USERNAME = connection_parameters['user']
PASSWORD = connection_parameters['password']
ROLE = connection_parameters['role']
WAREHOUSE = connection_parameters['warehouse']
DATABASE = connection_parameters['database']
SCHEMA = connection_parameters['schema']

# Cortex analyst:
SEMANTIC_STAGE = 'SEMANTIC_FILES'
SEMANTIC_FILE = 'semantic_search_tags_19.yaml'

# Cortex search:
SEARCH_SERVICE_NAME = 'SEARCH_TICKET_SUMMARY_DESCRIPTION'



session = Session.builder.configs(connection_parameters).create()
st.session_state.session = session
st.session_state.token = session.connection.rest.token
st.session_state.messages = []





def askAI(prompt): 
    sql = "SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', '" + prompt + "')"
    airesp = session.sql(sql).collect()
    return airesp[0][0]

def cortex_complete(prompt): 
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2',{prompt}, {{'temperature': 0.7}})"
    airesp = session.sql(sql).collect()
    return airesp[0][0]


def perform_search_service(user_query, filters={}, limit=10):
    request_headers = {
        "Authorization": f'Snowflake token="{session.connection.rest.token}"',
        "Content-Type": "application/json"
    }
    
    request_body = {
        "query": user_query,
        "columns": [
            'ID',
            'CUSTOMER_NAME',
            'SUMMARY',
            'ISSUE_KEY',
            'ISSUE_ID',
            'ISSUE_TYPE',
            'STATUS',
            'PROJECT_KEY',
            'PROJECT_NAME',
            'PROJECT_TYPE',
            'PROJECT_LEAD',
            'PROJECT_LEAD_ID',
            'PRIORITY',
            'RESOLUTION',
            'ASSIGNEE',
            'ASSIGNEE_ID',
            'REPORTER',
            'REPORTER_ID',
            'CREATOR',
            'CREATOR_ID',
            'CREATED',
            'UPDATED',
            'LAST_VIEWED',
            'RESOLVED',
            'DUE_DATE',
            'VOTES',
            'DESCRIPTION',
            'ENVIRONMENT',
            'WATCHERS',
            'WATCHERS_ID',
            'PARENT',
            'PARENT_SUMMARY',
            'STATUS_CATEGORY',
            'STATUS_CATEGORY_CHANGED',
            'SENTIMENT',
            'AI_SUMMARY'
        ],
        "filter": filters,
        "limit": limit,
        "experimental": {}
    }
    
    resp = requests.post(
        url=f"{HOST}/api/v2/databases/{DATABASE}/schemas/{SCHEMA}/cortex-search-services/{SEARCH_SERVICE_NAME}:query",
        json=request_body,
        headers=request_headers
    )
    
    return resp.json()
    # st.dataframe(resp.json())




def perform_analyst_search(user_query, filters):
    response = {
        'status': 000,
        'sql': '',
        'table_data':'',
        'ai_response': ''
    }
    
    request_headers = {
        "Authorization": f'Snowflake token="{session.connection.rest.token}"',
        "Content-Type": "application/json"
    }
    
    request_body = {   
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_query + 'where filters = ' + str(filters)
                    }
                ]
            },
        ],
        "semantic_model_file": f'@{DATABASE}.{SCHEMA}.{SEMANTIC_STAGE}/{SEMANTIC_FILE}'
    }
    
    resp = requests.post(
        url=f"{HOST}/api/v2/cortex/analyst/message",
        json=request_body,
        headers=request_headers
    )

    response['status'] = resp.status_code    
    
    if resp.status_code < 400:
        resp = resp.json()
        request_id = resp["request_id"]
        content = resp["message"]["content"]
        response['raw'] = content
        sql = ''
        
        for item in content:
            if item["type"] == "sql":
                sql = item["statement"]
                response['sql'] = sql
                query = session.sql(sql).collect()
                response['table_data'] = query
                
                data = str(query).replace("'", "")
                
                print(sql)
                print('\n--------------------------------------------------------------')
                
                if data != '[]':
                
                    prompt = f"""Summarize and anwswer the question in consise and clear terms like a professional from the given raw data.
                                QUESTION: \n {user_query}\n
                                Unstructured Data: \n{data}
                            """
                    
                    print(prompt)
                    print('\n--------------------------------------------------------------')
                    
                    airesp = askAI(prompt)
                    response['ai_response'] = airesp
                    response['is_valid'] = True
                
                else:
                    response['ai_response'] = 'Sorry! I couldnt find an answer to your query'
                    response['is_valid'] = False

            elif item["type"] == "text":
                response['ai_response'] = item['text']
                response['is_valid'] = False
            
            print(response['ai_response'])
            
        # if sql != '':
        #     query = session.sql(sql).collect()
        #     response['table_data'] = query
        #     # st.write(query)
            
        #     data = str(query).replace("'", "")
            
        #     prompt = f'Summarize and anwswer the question in consise and clear terms like a professional from the given raw data. QUESTION: \n {user_query} \n Unstructured Data: \n{data}'
        #     airesp = askAI(prompt)
        #     response['ai_response'] = airesp
        #         # st.write(airesp)
    
    return response     


def ai_summarize(prompt, data):
    data = str(data).replace("'", "")
    prompt = prompt.replace("'", "")
    
    prompt = f'You are support agent who work for a Saas company. Your job is to analyse, understand and summarize customer feedbacks and tickets to support the internal teams to work effeciently. Summarize and anwswer the question in consise and clear terms like a professional from the given raw data. carefully go through the questions and provide exceptionally good answer. QUESTION: \n {prompt} \n Unstructured Data: \n{data}. Provide the response in a markdown format.'
    airesp = askAI(prompt)
    
    return airesp


def restAPI():
    user_query = st.session_state.search_input
    
    if user_query != '':
        search = perform_analyst_search(user_query = user_query, filters={})
        st.markdown(search)
    
    else:
        st.session_state.messages.append("No message given")



def fetch_table_data(query):
    return session.sql(query)


def get_all_customers():
    resp = session.sql("""select * from tickets""")
    return resp

#---------------------------------------------------------------------------------------------


# searchData = st.text_input("Search for data in natural language", key="search_input", on_change=restAPI, args=None)


# st.checkbox(label='summarize response with AI (uncheck if not needed)', value=False, key='summarize')
# st.selectbox('semantic file:', options=["semantic_search_2.yaml"], key="semantic_file")

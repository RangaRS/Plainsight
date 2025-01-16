import streamlit as st
from database import perform_analyst_search, perform_search_service, ai_summarize
   
        

st.session_state.messages = []
    
        
def render_chat(filters, summarize=False):
    st.subheader("AI Chatbot")
    message_container = st.container(height=600)
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
    for history in st.session_state.messages:
        message_container.chat_message(history['role']).markdown(history['message'])
    
    prompt = st.chat_input("Ask me something")
    
    st.selectbox(label='select search mode:', options=['Cortex Search', 'Cortex Analyst', 'Complete'], key='searchMode')
    st.checkbox('Summarize Response', value=summarize, key='summarize')
    
    if prompt:
        st.session_state.messages.append({'role':'User', 'message': prompt})
        message_container.chat_message("User").write(prompt)
        
        with message_container:
            with st.spinner('Looking for an answer...'):
                ai_resp = ''
                if st.session_state.searchMode == 'Cortex Search':
                    ai_resp = perform_search_service(prompt, filters=filters)
                    
                    if st.session_state.summarize:
                        ai_resp = ai_summarize(prompt, ai_resp)
                        st.session_state.messages.append({'role':'AI', 'message': ai_resp})
                    else:    
                        st.session_state.messages.append({'role':'AI', 'message': ai_resp})
                        
                elif st.session_state.searchMode == 'Cortex Analyst':
                    ai_resp = perform_analyst_search(f"If unable to find it other columns, Try to look for the question majorly in description column for the possibility of occurance of any one of the key words. \nUSER-QUERY:{prompt} \n where filters = {str(filters)}".replace("'",""), summarize=st.session_state.summarize)
                
                with message_container.chat_message("AI"):
                    with st.expander('Generated SQL'):
                        st.code(ai_resp['sql'], language='sql')
                    with st.expander('Raw Data'):
                        st.write(ai_resp['raw_data'])
                    
                    st.markdown(ai_resp['ai_response'])
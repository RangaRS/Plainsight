import json
import streamlit as st
from database import perform_analyst_search, perform_search_service, ai_summarize, cortex_complete     

st.session_state.messages = []
        
def render_chat(filters =None):
    message_container = st.container(height=600)
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
    for history in st.session_state.messages:
        message_container.chat_message(history['role']).markdown(history['content'])
    
    prompt = st.chat_input("Ask me something")
        
    if prompt:
        system_prompt = {
            "role": "system",
            "content": (
                "You are a helpful assistant analyzing user problems with clarity for the internal team. "
                "You work for a B2B SaaS company called Sourcetree, focused on developer software. "
                "Respond with relevant insights based only on Sourcetree and its related content."
            ),
        }
            
        st.session_state.messages.append({'role':'User', 'content': prompt})
        message_container.chat_message("User").write(prompt)
        
        with message_container:
            with st.spinner('Looking for an answer...'):
                analyst_response = perform_analyst_search(f"""If unable to find it other columns,
                                                    Try to look for the question majorly in
                                                    summary or description column for the possibility
                                                    of occurance of any one of the key words. \n
                                                    USER-QUERY:{prompt} \n 
                                                    where filters = {str(filters)}
                                                    """.replace("'","")
                                                )
                    
                messageBundle = st.session_state.messages.copy()
                messageBundle.insert(0, system_prompt)
                
                if analyst_response['sql'] != '':
                    additional_info = analyst_response['ai_response']
                    formatted_text = f"""User Question: {prompt} \n Additional info: {additional_info}""".replace("'", "")
                                        
                    analyst_response = {'role':'user', 'content': formatted_text}
                    messageBundle.pop()                    
                    messageBundle.append(analyst_response)

                ai_response = cortex_complete(messageBundle)
                ai_answer = json.loads(ai_response)['choices'][0]['messages']
                st.session_state.messages.append({'role':'assistant', 'content': ai_answer.replace("'", "")})

                message_container.chat_message("assistant").markdown(ai_answer)
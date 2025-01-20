import streamlit as st
import Utils.components as components
from Utils.utils import calculate_sentiment_scores
from database import session, fetch_table_data, perform_analyst_search, perform_search_service, ai_summarize

@st.cache_data
def fetch_all_tags():
    return fetch_table_data(f"select * from tag").to_pandas()


def render_all_tags():
    tags_data = fetch_all_tags()
    issueTypes = tags_data[tags_data['TYPE'] == 'ISSUE_TYPE']
    moduleTypes = tags_data[tags_data['TYPE'] == 'MODULE']
    categoryTypes = tags_data[tags_data['TYPE'] == 'CATEGORY']
    
    issueTypesCount = issueTypes['NAME'].value_counts().reset_index().sort_values(by='count', ascending=False)
    issueTypesTotal = issueTypesCount['count'].sum()
    
    moduleTypesCount = moduleTypes['NAME'].value_counts().reset_index().sort_values(by='count', ascending=False)
    moduleTypesTotal = moduleTypesCount['count'].sum()
    
    categoryTypesCount = categoryTypes['NAME'].value_counts().reset_index().sort_values(by='count', ascending=False)
    categoryTypesTotal = categoryTypesCount['count'].sum()

    
    col1, col2, col3 = st.columns(3, border=True)
    with col1:
        with st.container(height=350, border=False):
            st.subheader('Tickets by Issue types')
            st.divider()
            
            for i, tag in issueTypesCount.iterrows():
                percent = round((tag['count']/issueTypesTotal)*100)
                
                st.html(f"<span class='tagLink'><a href='/tags?name={tag['NAME']}'>{tag['NAME']}</a> <span> {str(percent) + '%'}</span></span>")
                
                if percent > 80:
                    st.html(components.progress_bar(tag['count'], 'red'))
                elif percent > 50 and percent < 80:
                    st.html(components.progress_bar(tag['count'], 'orange'))
                else:
                    st.html(components.progress_bar(tag['count'], 'blue'))
    
    
    with col2:
        with st.container(height=350, border=False):
            st.subheader('Tickets by Modules')
            st.divider()
            
            for i, tag in moduleTypesCount.iterrows():
                percent = round((tag['count']/moduleTypesTotal)*100)
                
                st.html(f"<span class='tagLink'><a href='/tags?name={tag['NAME']}'>{tag['NAME']}</a> <span> {str(percent) + '%'}</span></span>")
                
                if percent > 80:
                    st.html(components.progress_bar(tag['count'], 'red'))
                elif percent > 50 and percent < 80:
                    st.html(components.progress_bar(tag['count'], 'orange'))
                else:
                    st.html(components.progress_bar(tag['count'], 'blue'))
    
    
    with col3:
        with st.container(height=350, border=False):
            st.subheader('Tickets by Categories')
            st.divider()
            
            for i, tag in categoryTypesCount.iterrows():
                percent = round((tag['count']/categoryTypesTotal)*100)
                
                st.html(f"<span class='tagLink'><a href='/tags?name={tag['NAME']}'>{tag['NAME']}</a> <span> {str(percent) + '%'}</span></span>")
                
                if percent > 80:
                    st.html(components.progress_bar(tag['count'], 'red'))
                elif percent > 50 and percent < 80:
                    st.html(components.progress_bar(tag['count'], 'orange'))
                else:
                    st.html(components.progress_bar(tag['count'], 'blue'))
    
    
    # for i, tag in issueTypesCount.iterrows():
        
    #     name, bar, count = st.columns([0.2,0.6, 0.2])
    #     percent = round((tag['count']/issueTypesTotal)*100)
        
    #     name.html(f"<span class='tagLink'><a href='/tags?name={tag['NAME']}'>{tag['NAME']}</a></span>")
    #     # bar.progress(tag['count'], '')
        
    #     if percent > 80:
    #         bar.html(components.progress_bar(tag['count'], 'red'))
    #     elif percent > 50 and percent < 80:
    #         bar.html(components.progress_bar(tag['count'], 'orange'))
    #     else:
    #         bar.html(components.progress_bar(tag['count'], 'blue'))
    #     count.write(f"{tag['count']} ({percent}%)")
        
    # st.bar_chart(issueTypesCount, x='NAME', horizontal=True)
    # st.bar_chart(moduleTypesCount, x='NAME', horizontal=True)
    # st.bar_chart(categoryTypesCount, x='NAME', horizontal=True)

@st.cache_data
def fetch_tickets(tagname):
    sql = f"select * from tickets where id in (select ticket_id from tag where name LIKE '%{tagname}%');"
    return session.sql(sql).to_pandas()
     

@st.cache_data
def summarize_data(tagname, data):
    
    overall_query = f"""select snowflake.cortex.complete('mistral-large2','You are an expert analyst specializing in identifying issues and opportunities for SaaS companies and provides a clean report with metrics and suggestions.
                                                                Given the provided customer support ticket information for the category {tagname}: provide a summary which you find suitable for auditing and reviewing purposes.
                                                                Try to combine similar tickets and decode the core issues.
                                                                DO NOT TALK ABOUT INDIVIDUAL TICKETS. ONLY PROVIDE GENERAL SUMMARY OF EVERYTHING COMBINED.
                                                                Input:
                                                                Ticket Details: {data}
                                                                Provide the whole response in not more than 250 words;
                                                                Response Format: Present your response in a well structured manner with right lines, spaces, and indentations. if possible in a markdown format.
                                                                ')"""

    summarize = session.sql(overall_query).collect()
    return summarize[0][0]
    
    
    
def render_tag_page(name):
    # st.title(f"# {name}")
    tickets = fetch_tickets(name)
    weighted_sentiment = calculate_sentiment_scores(tickets.get(['CREATED', 'SENTIMENT']))
    
    all_tickets_count = tickets['ID'].count()
    closed_tickets_count = tickets[tickets['RESOLUTION'].isin(['Fixed', 'Not a bug', 'Invalid'])]['ID'].count()
    open_tickets_count = all_tickets_count - closed_tickets_count
    
    st.html(components.customer_title_card(name, weighted_sentiment))
    
    overview_tab, all_tickets_tab = st.tabs(['Overview', 'All Tickets'])
    
    text = ''
    with all_tickets_tab:
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Total", value=str(all_tickets_count), border=True)
        col2.metric(label="Open", value=str(open_tickets_count), border=True)
        col3.metric(label="Closed", value=str(closed_tickets_count), border=True)
        
        for i,k in tickets.iterrows():
            text += ('customer name: ' + k['CUSTOMER_NAME'] + '\n Summary: ' + k['AI_SUMMARY'] + '\n status: ' + k['STATUS'] + '\n Sentiment: ' + k['SENTIMENT'])
            st.html(components.ticket_card(k))
            
    text = text.replace("'", "")
    summary = summarize_data(name, text)
    
    overview_tab.markdown(summary)
        

        
    
    
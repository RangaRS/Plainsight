import streamlit as st
import Utils.components as components
import plotly.express as px
from Module.Tags.tags import fetch_all_tags
from database import fetch_table_data, perform_analyst_search, perform_search_service, ai_summarize

def render_homepage(all_tickets):

    tags_data = fetch_all_tags()
    
    all_tickets_count = all_tickets['ID'].count()
    closed_tickets_count = all_tickets[all_tickets['RESOLUTION'].isin(['Fixed', 'Not a bug', 'Invalid'])]['ID'].count()
    open_tickets_count = all_tickets_count - closed_tickets_count
    
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total", value=str(all_tickets_count), border=True)
    col2.metric(label="Open", value=str(open_tickets_count), border=True)
    col3.metric(label="Closed", value=str(closed_tickets_count), border=True)
    
    issueTypes = tags_data[tags_data['TYPE'] == 'ISSUE_TYPE']
    # moduleTypes = tags_data[tags_data['TYPE'] == 'MODULE']
    # categoryTypes = tags_data[tags_data['TYPE'] == 'CATEGORY']
    
    issueTypesCount = issueTypes['NAME'].value_counts().reset_index().sort_values(by='count', ascending=False)
    issueTypesTotal = issueTypesCount['count'].sum()
    
    sentiment_split = all_tickets['SENTIMENT'].value_counts().reset_index()
    org_split = all_tickets['CUSTOMER_NAME'].value_counts().reset_index()
    ticks_range = all_tickets.get(['CREATED']).value_counts().reset_index()
    grouped_df = ticks_range.groupby(['CREATED'])['count'].sum().reset_index()
    pivot_df = grouped_df.pivot(index='CREATED', columns='count', values='count').fillna(0)
    monthly_df = pivot_df.resample('W').sum()
    monthly_df

    r1col1, r1col2 = st.columns([0.7, 0.3], border=True)

    with r1col1:
        st.subheader('Ticket Inflow Rate')
        st.divider()
        st.line_chart(monthly_df)
    
    with r1col2:
        st.subheader('Tickets by Customer')
        st.divider()
        total = org_split['count'].sum()
        
        with st.container(height=350, border=False):
            
            for i,org in org_split.iterrows():
                
                percent = round((org['count'] / total)*100)
                
                st.html(f"<span class='tagLink'><a href='/customers?orgname={org['CUSTOMER_NAME']}'>{org['CUSTOMER_NAME']}</a> <span> {str(percent) + '%'}</span></span>")

                if percent > 80:
                    st.html(components.progress_bar(percent, 'red'))
                elif percent > 50 and percent < 80:
                    st.html(components.progress_bar(percent, 'orange'))
                else:
                    st.html(components.progress_bar(percent, 'blue'))
    

    r2col1, r2col2= st.columns(2, border=True)

    with r2col1:
        st.subheader('Sentiment Splitup')
        st.divider()
        
        with st.container(height=350, border=False):
            # st.bar_chart(sentiment_split)
            sentiment_split.drop(sentiment_split.tail(2).index,inplace = True)
            labels = sentiment_split['SENTIMENT']
            values = sentiment_split['count']
            # Create the pie chart
            fig = px.pie(values=values, names=labels, hole=0.5, title='Pie Chart')

            # Display in Streamlit
            st.plotly_chart(fig, use_container_width=True)

    
    with r2col2:
        st.subheader('Tickets by Issue types')
        st.divider()
        
        with st.container(height=350, border=False):
            for i, tag in issueTypesCount.iterrows():
                percent = round((tag['count']/issueTypesTotal)*100)
                
                st.html(f"<span class='tagLink'><a href='/tags?name={tag['NAME']}'>{tag['NAME']}</a> <span> {str(percent) + '%'}</span></span>")
                
                if percent > 80:
                    st.html(components.progress_bar(tag['count'], 'red'))
                elif percent > 50 and percent < 80:
                    st.html(components.progress_bar(tag['count'], 'orange'))
                else:
                    st.html(components.progress_bar(tag['count'], 'blue'))
                    
    st.divider()
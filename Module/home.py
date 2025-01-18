import streamlit as st
import Utils.components as component
from database import fetch_table_data, perform_analyst_search, perform_search_service, ai_summarize

def render_homepage(all_tickets):
    issues_split = all_tickets['ISSUE_TYPE'].value_counts().reset_index()
    sentiment_split = all_tickets['SENTIMENT'].value_counts()
    status_split = all_tickets['STATUS'].value_counts()
    org_split = all_tickets['CUSTOMER_NAME'].value_counts()
    ticks_range = all_tickets.get(['CREATED']).value_counts().reset_index()
    grouped_df = ticks_range.groupby(['CREATED'])['count'].sum().reset_index()
    pivot_df = grouped_df.pivot(index='CREATED', columns='count', values='count').fillna(0)
    monthly_df = pivot_df.resample('W').sum()
    monthly_df

    col1, col2, col3 = st.columns(3, border=True)

    with col1:
        st.subheader('Ticket Inflow in the last year')
        st.divider()
        st.line_chart(monthly_df)
    
    with col2:
        st.subheader('Tickets by Customer')
        st.divider()
        st.bar_chart(org_split.sort_values())
    
    with col3:
        st.subheader('Tickets by Issue types')
        st.divider()
        
        for I, row in issues_split.iterrows():
            st.markdown(f"##### {row['ISSUE_TYPE']}")
            st.html(component.progress_bar(row['count'], 'green'))
            # st.progress(row['count'], '')
        # st.bar_chart(issues_split.sort_values())

    st.bar_chart(sentiment_split)
    st.bar_chart(status_split)
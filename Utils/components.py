import pandas as pd
from Utils.utils import date_to_words, time_to_words, get_sentiment_emotion

def ticket_card(ticket):
    
    resolution = ''
    classname = ''
    if ticket.RESOLUTION in [None, 'Duplicate']:
        resolution = 'Pending'
        classname = 'Pending'

    elif ticket.RESOLUTION in ['Not a bug', 'Fixed']:
        resolution = ticket.RESOLUTION
        classname = 'Fixed'

    
    resolution_component = chip(resolution, classes=classname+ ' resolution')
        
    return f"""<div data-id='{ticket.ID}' class="card-container"> 
                                <div class="title-section">
                                    <div class="ticket-card-title">
                                        <span class="ticket-summary">
                                            <a href='/tickets?ticketid={ticket.ID}'>#{ticket.ID} - {ticket.SUMMARY}</a>
                                            {resolution_component}
                                        </span>
                                    </div>
                                    <div class="ticket-info"><span class="date-readonly">Created on : {date_to_words(ticket.CREATED)}</span></div>
                                </div>

                                <span class="ticket-description">AI Summary: \n{ticket.AI_SUMMARY}</span>
                                <div class="chips">

                                    <span class="chip {ticket.PRIORITY}">{ticket.PRIORITY}</span>
                                    <span class="chip {ticket.CUSTOMER_NAME}">{ticket.CUSTOMER_NAME}</span>
                                    <span class="chip {ticket.STATUS}">{ticket.STATUS}</span>
                                    <span class="chip {ticket.ISSUE_TYPE}">{ticket.ISSUE_TYPE}</span>
                                </div>
                            </div>                
                        """


def customer_title_card(titleName, sentiments):
    
    tagGroup = ''
    
    for i,s in sentiments.iterrows():
        if s['SCORE'] > 0:
            sentiment = get_sentiment_emotion(s['SENTIMENT'])
            score = str(round(s['SCORE'])) + '%'
                
            tagGroup += tag(s['SENTIMENT'] + ' ' + score, sentiment)
    
    # print(tagGroup) 
    
    return f"""<div class="title-card">
                    <div class="image">{titleName[:2]}</div>
                    <div class="titleGroup">
                        <span class="titleName">{titleName}</span>
                        <div class="tag-group">{tagGroup}</div>
                </div>
            </div>
            """
            
            
def ticket_title_card(ticket, tags):
    
    issue_type = ''
    module = ''
    category = ''
    resolution = ''
    
    for k,v in tags:
        if k == 'ISSUE_TYPE':
            for t in v:
                issue_type += chip(t)
        
        elif k == 'MODULE':
            for t in v:
                module += chip(t)

        elif k == 'CATEGORY':
            for t in v:
                category += chip(t)

    resolution = ''
    classname = ''
    if ticket.RESOLUTION in [None, 'Duplicate']:
        resolution = 'Pending'
        classname = 'Pending'

    elif ticket.RESOLUTION in ['Not a bug', 'Fixed']:
        resolution = ticket.RESOLUTION
        classname = 'Fixed'

    
    resolution_component = chip(resolution, classes=classname+ ' resolution')
    
    return f"""<div class="ticket-header-card">
                <span class="ticket-header-title">#{ticket.ID} - {ticket.SUMMARY} {resolution_component}</span>
                <div class="ticket-sub">
                    <span class="chip {ticket.CUSTOMER_NAME}">{ticket.CUSTOMER_NAME}</span>
                    <span class="chip {ticket.PRIORITY}">{ticket.PRIORITY}</span>
                </div>
                {table_cell('Issue Type', issue_type)}           
                {table_cell('Module', module)}           
                {table_cell('Category', category)}                                      
                {table_cell('Sentiment', tag(ticket.SENTIMENT, get_sentiment_emotion(ticket.SENTIMENT)))}                                      
                <span class="section-title">Description:</span>
                <span class="ticket-description">{ticket.DESCRIPTION}</span>
                </div>"""
                
                
def progress_bar(value, color):
    return f"""
            <div class="progress_bar">
                <div style="width: {value}%;" class="progress {color}"></div>
            </div>
            """
            
def tag(content, type):
    return f"""
                <div class="tag {type}">{content}</div>
            """


def chip(content, classes=''):
    return f"""<span class="chip {classes}">{content}</span>"""          

def comment_card(comment):
    approved = ''
    status = ''
    if comment.IS_RESOLVED:
        approved = '<span class="chip approved">Approved Comment</span>'
        status = 'approved'
        
    return f"""
            <div class="comment-container {status}">
            <div style="display:flex; flex-direction: row; gap: 8px; align-items: center;">
                <div class="profile-picture"></div>
                    <div class="comment-title-group">
                        <span class="username">Sree Rengavasan {approved}</span>
                        <span class="addedDate">{date_to_words(comment.UPDATED)}</span>
                    </div>
                </div>
                <span class="comment">{comment.COMMENT}</span>
            </div>
            """


def customer_card_mini(name, count):
    return f"""
            <div class="customer-card-mini">
                <div class="image">{name[:1]}</div>
                <span class="title">{name}</span>
                <span class="count">{count}</span>
            </div>

            """
            
            
def table_cell(key, value):
    
    if isinstance(value, pd.Timestamp):
        value = date_to_words(value)
    
    if type(key) != 'str':
        key = str(key)
    
    if type(value) != 'str':
        value = str(value)
     
    return f"""
            <div class="key-value-group">
                <span class="cell key">{key}</span>
                <span class="cell">:</span>
                <span class="cell value">{str(value)}</span>
            </div>

            """
            
            
def thumbnail(content, height=40):
    return f"""
            <div style="height: {height}px" class="thumbnail">
                <span>{content}</span>
            </div>
            """
            

def sentiment_widget(title, count, height, emoji):
    return f"""
            <div class="sentiment-widget">
                {thumbnail(emoji, height)}
                <div class="sentiment-group">
                    <span class="title">{title}</span>
                    <span class="count">Total tickets : {count}</span>
                </div>
            </div>
            """
            

def ai_summary(content):
    return f""" <div class="ai-summary-container">
                <span class="title">AI Generated Answer</span>
                <span class="answer">{content}</span>
                <span class="caution-text">This AI-generated suggestion is a starting point; validate it with the respective team for safety.</span>
            </div>
            """
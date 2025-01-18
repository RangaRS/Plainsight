from Utils.utils import date_to_words, time_to_words

def ticket_card(ticket):
    
    resolution = ''
    if ticket.RESOLUTION == None:
        resolution = 'Pending'
        
    elif ticket.RESOLUTION == 'Fixed':
        resolution = 'Resolved'
    
    else:
        resolution = ticket.RESOLUTION
        
    return f"""<div data-id='{ticket.ID}' class="card-container"> 
                                <div class="title-section">
                                    <div class="ticket-title">
                                        <span class="ticket-summary">
                                            <a href='/tickets?ticketid={ticket.ID}'>#{ticket.ID} - {ticket.SUMMARY}</a>
                                        </span>
                                    </div>
                                    <div class="ticket-info"><span class="date-readonly">Created on : {ticket.CREATED}</span></div>
                                </div>

                                <span class="ticket-description">AI Summary: \n{ticket.AI_SUMMARY}</span>
                                <div class="chips">
                                    <span class="chip {resolution}">{resolution}</span>
                                    <span class="chip {ticket.PRIORITY}">{ticket.PRIORITY}</span>
                                    <span class="chip {ticket.CUSTOMER_NAME}">{ticket.CUSTOMER_NAME}</span>
                                    <span class="chip {ticket.STATUS}">{ticket.STATUS}</span>
                                    <span class="chip {ticket.ISSUE_TYPE}">{ticket.ISSUE_TYPE}</span>
                                </div>
                            </div>                
                        """


def customer_title_card(titleName, sentiments):
    negativeList = ['annoyance', 'disappointment']
    moderateList = ['confusion', 'curiosity']
    
    tagGroup = ''
    
    for i,s in sentiments.iterrows():
        if s['SCORE'] > 0:
            sentiment = ''
            score = str(round(s['SCORE'])) + '%'
            
            if s['SENTIMENT'] in negativeList:
                sentiment = 'negative'
            elif s['SENTIMENT'] in moderateList:
                sentiment = 'moderate'
            else:
                sentiment = 'neutral'
                
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
            
            
def ticket_title_card(ticket):
    return f"""<div class="ticket-detail-card">
                <span class="ticket-title">{ticket.SUMMARY}</span>
                <div class="ticket-sub">
                    <span class="chip {ticket.PRIORITY}">{ticket.PRIORITY}</span>
                    <span class="chip">{ticket.ISSUE_TYPE}</span>
                    <span class="chip">{ticket.STATUS}</span>
                </div>
                <table class="ticket-details">
                    <tr><td width="100px">Reporter</td><td width="10px">:</td><td>{ticket.CUSTOMER_NAME}</td></tr>
                    <tr><td>Reporter</td><td>:</td><td>Amazon</td></tr>
                    <tr><td>Reporter</td><td>:</td><td>Amazon</td></tr>
                    <tr><td>Reporter</td><td>:</td><td>Amazon</td></tr>
                    <tr><td>Reporter</td><td>:</td><td>Amazon</td></tr>
                </table>
                
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
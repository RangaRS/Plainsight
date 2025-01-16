
def ticket_card(ticket):
    return f"""<div data-id='{ticket.ID}' class="card-container"> 
                                <div class="title-section">
                                    <div class="ticket-title"><span class="ticket-summary"><a href='/tickets?ticketid={ticket.ID}'>#{ticket.ID} - {ticket.SUMMARY}</a></span></div>
                                    <div class="ticket-info"><span class="date-readonly">{ticket.CREATED}</span> | <span class="date-readonly">{ticket.UPDATED}</span></div>
                                </div>

                                <span class="ticket-description">AI Summary: \n{ticket.AI_SUMMARY}</span>
                                <div class="chips"><span class="chip {ticket.CUSTOMER_NAME}">{ticket.CUSTOMER_NAME}</span><span class="chip {ticket.STATUS}">{ticket.STATUS}</span><span class="chip {ticket.ISSUE_TYPE}">{ticket.ISSUE_TYPE}</span></div>
                            </div>                
                        """


def customer_title_card(orgname, sentiment, duration):
    return f"""<div class="titleGroup">
                    <span class="orgname">{orgname}</span><span class="sentiment-chip">Sentiment: {sentiment}</span><span style="font-size: 14px; opacity: 0.6;">{duration}</span>
                </div>"""
            
            
def ticket_title_card(ticket):
    return f"""<div class="ticket-detail-card">
                <span class="ticket-title">{ticket.SUMMARY}</span>
                <div class="ticket-sub">
                    <span class="priority-chip {ticket.PRIORITY}">{ticket.PRIORITY}</span>
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
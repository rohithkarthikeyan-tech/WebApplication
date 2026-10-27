import re
import os
import logging
from django.db.models import Q
from .models import FAQ, ErrorCode, SupportTicket
from .mongo import save_chat_log

logger = logging.getLogger('website.assistant')


def find_matching_error_code(query_text):
    """
    Checks if the user's message is asking about a known error code (400, 401, 403, 404, 429, 500, 503, 480).
    """
    # Regex for standard 3-digit error codes
    code_match = re.search(r'\b(400|401|403|404|429|500|503|480)\b', query_text)
    if code_match:
        code_num = int(code_match.group(1))
        error_obj = ErrorCode.objects.filter(code=code_num).first()
        if error_obj:
            return error_obj

    # Check for keywords like "bad request", "forbidden", "not found", "quantum sync"
    lower_query = query_text.lower()
    keyword_map = {
        'bad request': 400,
        'unauthorized': 401,
        'forbidden': 403,
        'permission denied': 403,
        'not found': 404,
        'rate limit': 429,
        'too many requests': 429,
        'internal server error': 500,
        'server error': 500,
        'service unavailable': 503,
        'quantum sync': 480,
        'neural link': 480,
    }
    for kw, code_num in keyword_map.items():
        if kw in lower_query:
            return ErrorCode.objects.filter(code=code_num).first()

    return None


def search_faqs_in_sql(query_text):
    """
    Queries the SQL database for matching FAQ entries using full token and keyword scoring.
    """
    words = [w.strip() for w in re.findall(r'\b\w{3,}\b', query_text.lower())]
    if not words:
        return None, 0

    active_faqs = FAQ.objects.filter(is_active=True)
    best_faq = None
    best_score = 0

    for faq in active_faqs:
        score = 0
        q_lower = faq.question.lower()
        ans_lower = faq.answer.lower()
        kw_lower = faq.keywords.lower()

        for word in words:
            # Question matches have highest weight
            if word in q_lower:
                score += 5
            # Keyword matches have high weight
            if word in kw_lower:
                score += 3
            # Body matches have standard weight
            if word in ans_lower:
                score += 1

        if score > best_score:
            best_score = score
            best_faq = faq

    return best_faq, best_score


def create_support_ticket_from_chat(name, email, subject, description, error_code=None):
    """
    Creates and saves a support ticket in the SQL database.
    """
    ticket = SupportTicket.objects.create(
        name=name or 'Anonymous User',
        email=email or 'user@aether-support.local',
        subject=subject or 'AI Assistant Escalated Ticket',
        description=description,
        source='AI Assistant',
        associated_error_code=error_code,
        priority='High' if error_code in [500, 503, 480] else 'Medium',
        status='Open'
    )
    return ticket


def ask_assistant(user_message, session_id='anonymous', context=None, user=None):
    """
    Main AI Assistant dispatch engine:
    1. Explains error codes from SQL ErrorCode model
    2. Answers questions from SQL FAQ model
    3. Handles ticket creation commands or triggers ticket escalation if unable to answer
    4. Persists the dialogue into MongoDB (or in-memory fallback)
    """
    query = (user_message or '').strip()
    lower_query = query.lower()

    response_data = {
        'reply': '',
        'intent': 'general',
        'can_answer': True,
        'matched_source': None,
        'suggest_ticket': False,
        'ticket_created': None,
    }

    # 1. Greetings
    if lower_query in ['hi', 'hello', 'hey', 'greetings', 'start', 'help']:
        response_data['reply'] = (
            "Hello! I am **Aether AI Assistant**.\n\n"
            "I can assist you with:\n"
            "• **Knowledgebase Queries**: Answers directly from our SQL database FAQs.\n"
            "• **Error Code Diagnostics**: Clear explanations and resolutions for HTTP 400, 401, 403, 404, 429, 500, 503, and our custom 480.\n"
            "• **Support Ticket Escalation**: I can automatically file a formal support ticket in SQL for our team.\n\n"
            "How can I help you today?"
        )
        response_data['intent'] = 'greeting'
        save_chat_log(session_id, query, response_data['reply'], intent='greeting')
        return response_data

    # 2. Check for explicit Support Ticket creation request
    ticket_triggers = ['create ticket', 'open ticket', 'file ticket', 'support ticket', 'escalate', 'contact support', 'submit ticket']
    if any(trigger in lower_query for trigger in ticket_triggers):
        # User wants a ticket
        user_name = user.get_full_name() or user.username if (user and user.is_authenticated) else 'Guest User'
        user_email = user.email if (user and user.is_authenticated and user.email) else 'guest@aether.local'
        subject = f"Support Request from Chat: {query[:45]}"
        description = f"User initiated ticket creation from Assistant session '{session_id}'. Query: {query}"

        # Check if context had an error code
        err_code = context.get('error_code') if context else None

        ticket = create_support_ticket_from_chat(
            name=user_name,
            email=user_email,
            subject=subject,
            description=description,
            error_code=err_code
        )

        response_data['reply'] = (
            f"✅ **Support Ticket Created!**\n\n"
            f"• **Ticket Number**: `{ticket.ticket_number}`\n"
            f"• **Status**: {ticket.status}\n"
            f"• **Priority**: {ticket.priority}\n"
            f"• **Assigned Storage**: SQL Database (`website_supportticket`)\n\n"
            f"Our engineering team has received your ticket and will follow up shortly."
        )
        response_data['intent'] = 'ticket_created'
        response_data['ticket_created'] = {
            'ticket_number': ticket.ticket_number,
            'status': ticket.status,
            'priority': ticket.priority,
        }
        save_chat_log(session_id, query, response_data['reply'], intent='ticket_created')
        return response_data

    # 3. Check for Error Code Inquiries
    error_obj = find_matching_error_code(query)
    if error_obj:
        response_data['reply'] = (
            f"### 🛡️ Error Code {error_obj.code}: {error_obj.title}\n\n"
            f"**Category:** {error_obj.category}\n\n"
            f"**What Happened:**\n{error_obj.description}\n\n"
            f"**Recommended Action / Resolution:**\n{error_obj.resolution}\n\n"
            f"> *AI Diagnostic Context:* {error_obj.ai_guidance}\n\n"
            f"If this error prevents you from completing your work, reply **'Create ticket'** and I will immediately log a support ticket in our SQL database."
        )
        response_data['intent'] = 'error_explanation'
        response_data['matched_source'] = f"ErrorCode {error_obj.code}"
        save_chat_log(session_id, query, response_data['reply'], intent=f'error_{error_obj.code}')
        return response_data

    # 4. Search FAQ Database in SQL
    best_faq, score = search_faqs_in_sql(query)
    if best_faq and score >= 4:
        response_data['reply'] = (
            f"### 💡 {best_faq.question}\n\n"
            f"{best_faq.answer}\n\n"
            f"*(Knowledge Source: SQL FAQ Database &bull; Category: {best_faq.category})*\n\n"
            f"Did this answer your question, or would you like to open a support ticket?"
        )
        response_data['intent'] = 'faq_answer'
        response_data['matched_source'] = f"FAQ #{best_faq.id}: {best_faq.question}"
        save_chat_log(session_id, query, response_data['reply'], intent='faq_match')
        return response_data

    # 5. Cannot Answer - Trigger Support Ticket Offer
    # Requirement: "creates a support ticket when it cannot answer"
    suggested_subject = f"Unresolved Inquiry: {query[:50]}"
    response_data['can_answer'] = False
    response_data['suggest_ticket'] = True
    response_data['intent'] = 'unresolved_fallback'

    response_data['reply'] = (
        "I searched our SQL knowledgebase and diagnostic error codes, but I could not find a verified answer to your specific query:\n\n"
        f"> *\"{query}\"*\n\n"
        "Would you like me to automatically **create a Support Ticket** for our engineering team to review this issue? "
        "Simply reply **'Yes, create a ticket'** or click the **'Create Support Ticket'** button below."
    )

    save_chat_log(session_id, query, response_data['reply'], intent='unresolved')
    return response_data

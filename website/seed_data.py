"""
Initial data seeder for Aether platform:
Populates at least 10 FAQs and 8 Error Codes into the SQL database.
"""

from .models import FAQ, ErrorCode

INITIAL_FAQS = [
    {
        'question': 'What is Aether and how is it architected?',
        'category': 'General',
        'keywords': 'architecture, platform, django, python, tech stack, sqlite',
        'answer': 'Aether is an enterprise-grade full-stack web platform built on Django 6.1 with SQLite for structured data (users, FAQs, support tickets) and MongoDB for document-oriented telemetry (chat conversation logs, user feedback, and request timings). It combines fluid glassmorphic styling with high security.',
        'order': 1,
    },
    {
        'question': 'How does user registration and authentication work?',
        'category': 'Authentication',
        'keywords': 'register, login, password, auth, session, dashboard',
        'answer': 'Users register with a unique username, verified email, and strong password (minimum 8 characters). Django authenticates sessions using secure HTTP-only cookies and hashes passwords using PBKDF2 with SHA-256. Authenticated users gain access to the protected Dashboard.',
        'order': 2,
    },
    {
        'question': 'What causes an HTTP 403 Forbidden error?',
        'category': 'Error Codes',
        'keywords': '403, forbidden, csrf, permission, access denied',
        'answer': 'HTTP 403 occurs when the server understands who you are or what was requested, but refuses to authorize the operation. Common causes include missing or invalid CSRF tokens in POST requests, accessing admin pages without staff privileges, or trying to view another user’s protected resources.',
        'order': 3,
    },
    {
        'question': 'What is HTTP 404 Not Found and how do I resolve it?',
        'category': 'Error Codes',
        'keywords': '404, not found, broken link, missing page, route',
        'answer': 'HTTP 404 indicates that the requested URL path does not match any route registered in Django’s urlpatterns. Check your URL spelling, use the navigation menu to return home, or ask the AI Assistant on the 404 page for automated redirection and ticket escalation.',
        'order': 4,
    },
    {
        'question': 'What is error code 480 (Aether Quantum Sync Failure)?',
        'category': 'Error Codes',
        'keywords': '480, custom code, site-specific, quantum sync, neural link, desynchronization',
        'answer': 'HTTP 480 is Aether’s site-specific custom error code. It represents an asynchronous data handshake phase drift where local client state and backend cluster telemetry fall out of harmony. Resolution involves refreshing session tokens or invoking the AI Assistant for auto-recalibration.',
        'order': 5,
    },
    {
        'question': 'How does the AI Assistant help me troubleshoot issues?',
        'category': 'AI Assistant',
        'keywords': 'ai, assistant, bot, chat, help, support, query, explain',
        'answer': 'The floating AI Assistant is available on every page. It parses the SQL FAQ knowledgebase to answer common inquiries, explains any of our 8 supported error codes with step-by-step remedies, and can automatically generate a Support Ticket in SQL if it cannot resolve your question.',
        'order': 6,
    },
    {
        'question': 'How does the system create and track support tickets?',
        'category': 'General',
        'keywords': 'ticket, support, helpdesk, issue, escalation, problem',
        'answer': 'Support tickets are stored in the SQL database with a unique alphanumeric reference (e.g. TICK-XXXX). They can be generated manually via the support portal or automatically escalated by the AI Assistant when a user’s inquiry cannot be answered directly.',
        'order': 7,
    },
    {
        'question': 'Where are chat conversation logs and feedback stored?',
        'category': 'Architecture',
        'keywords': 'mongodb, chat logs, feedback, database, storage, nosql',
        'answer': 'In compliance with modern polyglot persistence architecture, transactional relational models (FAQs, tickets, users) live in SQL, while unstructured event streams, AI conversation logs, and thumbs-up/down ratings are recorded into MongoDB collections (with local memory fallback).',
        'order': 8,
    },
    {
        'question': 'How does CSRF protection work on forms?',
        'category': 'Security',
        'keywords': 'csrf, token, security, attack, form, post, protection',
        'answer': 'Every POST form (contact, login, registration, support tickets) requires a cryptographic {% csrf_token %} rendered by Django. The CsrfViewMiddleware inspects this nonce against session cookies to prevent cross-site malicious request hijacking.',
        'order': 9,
    },
    {
        'question': 'What is HTTP 429 Too Many Requests?',
        'category': 'Error Codes',
        'keywords': '429, rate limit, too many requests, quota, throttle',
        'answer': 'HTTP 429 signals that an IP address or user session has exceeded the maximum permitted request threshold within a given time period. Wait a few moments before retrying, or contact support if you require higher enterprise rate quotas.',
        'order': 10,
    },
    {
        'question': 'What does HTTP 500 Internal Server Error mean?',
        'category': 'Error Codes',
        'keywords': '500, server error, crash, bug, exception, internal',
        'answer': 'HTTP 500 means the server encountered an unexpected runtime exception while processing your request. Our custom 500 page includes an instant "Ask the Assistant" option to immediately capture stack diagnostics and dispatch a high-priority support ticket.',
        'order': 11,
    },
    {
        'question': 'What is the Health Check page and what telemetry does it show?',
        'category': 'Architecture',
        'keywords': 'health, healthcheck, status, uptime, latency, third party, api',
        'answer': 'The /health/ endpoint delivers real-time operational telemetry. It verifies SQL database connectivity, checks MongoDB connection status, measures external third-party API latency with timeout protection, and calculates server uptime.',
        'order': 12,
    },
]

INITIAL_ERROR_CODES = [
    {
        'code': 400,
        'title': 'Bad Request',
        'category': 'Client Error',
        'summary': 'The server cannot process the request due to malformed syntax or invalid parameters.',
        'description': 'HTTP 400 indicates that the client request contained invalid data, corrupted query strings, or missing required payload fields that the Django serializer could not parse.',
        'resolution': 'Verify the syntax of your request, check form field validation requirements, and ensure JSON payloads are properly formatted.',
        'ai_guidance': 'Advise the user to inspect form field inputs for missing required values or illegal characters. Offer to review the submitted payload.',
    },
    {
        'code': 401,
        'title': 'Unauthorized',
        'category': 'Client Error',
        'summary': 'Authentication is required and has either failed or has not yet been provided.',
        'description': 'HTTP 401 signals that access to the requested view or API endpoint requires valid user credentials, but no active Django session or auth token was supplied.',
        'resolution': 'Log in with valid account credentials at /login/ or ensure your session cookie is being transmitted.',
        'ai_guidance': 'Direct the user to the /login/ page. Explain that protected portals require an active authenticated session.',
    },
    {
        'code': 403,
        'title': 'Forbidden',
        'category': 'Client Error',
        'summary': 'The server understood the request, but refuses to authorize access.',
        'description': 'HTTP 403 indicates permission denial. Common triggers in Django include CSRF verification failures, attempting to access staff/admin views without permissions, or restricted operations.',
        'resolution': 'Ensure cookies are enabled in your browser so CSRF tokens function, or contact an administrator if you require elevated role permissions.',
        'ai_guidance': 'Explain CSRF protection and role-based permissions. Suggest clearing cookies or logging in as an administrator.',
    },
    {
        'code': 404,
        'title': 'Not Found',
        'category': 'Client Error',
        'summary': 'The server cannot locate the requested URI or database resource.',
        'description': 'HTTP 404 is returned when the incoming request path does not match any URL pattern defined in ROOT_URLCONF or when an ORM object query (get_object_or_404) returns no record.',
        'resolution': 'Check the URL spelling in your address bar, verify the resource ID, or navigate back to the home page.',
        'ai_guidance': 'Help the user identify the intended page. Recommend navigation links (Home, FAQs, About, Contact) or create a ticket if a link is broken.',
    },
    {
        'code': 429,
        'title': 'Too Many Requests',
        'category': 'Client Error',
        'summary': 'The client has exceeded the rate limit threshold for requests.',
        'description': 'HTTP 429 is triggered by rate limiting middleware when a client sends more requests than permitted within a rolling time window, safeguarding backend stability.',
        'resolution': 'Pause execution and implement an exponential backoff before retrying your requests.',
        'ai_guidance': 'Advise the user to wait 30-60 seconds before making additional requests. If automated scripts are running, recommend lowering concurrency.',
    },
    {
        'code': 500,
        'title': 'Internal Server Error',
        'category': 'Server Error',
        'summary': 'An unexpected condition prevented the server from fulfilling the request.',
        'description': 'HTTP 500 indicates an unhandled server-side exception occurred during view execution, template rendering, or database interaction.',
        'resolution': 'Retry the request after a moment. If the issue persists, trigger "Ask the Assistant" to immediately file a support ticket.',
        'ai_guidance': 'Apologize for the inconvenience, capture the URL and error context, and offer to automatically generate an urgent support ticket.',
    },
    {
        'code': 503,
        'title': 'Service Unavailable',
        'category': 'Server Error',
        'summary': 'The server is temporarily overloaded or down for scheduled maintenance.',
        'description': 'HTTP 503 signals that the backend service or upstream microservice is temporarily unable to handle the request due to maintenance or capacity bottlenecks.',
        'resolution': 'Check the /health/ telemetry dashboard for system status and retry after a short delay.',
        'ai_guidance': 'Inform the user of possible maintenance or temporary load. Suggest checking the /health/ page for real-time subsystem status.',
    },
    {
        'code': 480,
        'title': 'Aether Quantum Sync Failure',
        'category': 'Site-Specific',
        'summary': 'Site-specific custom error: Client-server session telemetry desynchronized.',
        'description': 'HTTP 480 is Aether’s proprietary custom error status. It is raised when client state telemetry and backend persistence clusters experience quantum phase divergence during asynchronous operations.',
        'resolution': 'Initiate a forced session re-synchronization by clicking "Ask the Assistant" or re-logging into your account portal.',
        'ai_guidance': 'Explain that 480 is Aether\'s proprietary error code for session desync. Guide them to re-authenticate or click "Ask the Assistant" to recalibrate.',
    },
]


def seed_initial_data():
    """
    Populates FAQs and ErrorCodes if tables are empty.
    """
    seeded_faqs = 0
    seeded_errors = 0

    if FAQ.objects.count() < 10:
        for item in INITIAL_FAQS:
            obj, created = FAQ.objects.get_or_create(
                question=item['question'],
                defaults={
                    'category': item['category'],
                    'keywords': item['keywords'],
                    'answer': item['answer'],
                    'order': item['order'],
                    'is_active': True,
                }
            )
            if created:
                seeded_faqs += 1

    if ErrorCode.objects.count() < 8:
        for item in INITIAL_ERROR_CODES:
            obj, created = ErrorCode.objects.get_or_create(
                code=item['code'],
                defaults={
                    'title': item['title'],
                    'category': item['category'],
                    'summary': item['summary'],
                    'description': item['description'],
                    'resolution': item['resolution'],
                    'ai_guidance': item['ai_guidance'],
                }
            )
            if created:
                seeded_errors += 1

    return seeded_faqs, seeded_errors

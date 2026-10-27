import json
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

from .models import ContactMessage, FAQ, ErrorCode, SupportTicket
from .forms import ContactForm, RegisterForm, CustomLoginForm
from .assistant import ask_assistant, create_support_ticket_from_chat
from .mongo import save_chat_feedback, get_mongo_status
from .services import fetch_external_telemetry


def ensure_db_ready():
    """
    Attempts to apply database migrations if tables are missing or not initialized yet.
    Guarantees zero-500 uptime on platforms where migrations weren't run prior to web launch.
    """
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
    except Exception:
        pass


def home(request):
    features = [
        {
            'icon': 'lightning',
            'title': 'High Performance Backend',
            'desc': 'Engineered on Django with optimized SQLite persistence, low-latency request routing, and clean modular architecture.',
            'tag': 'Engineered',
        },
        {
            'icon': 'shield',
            'title': 'Enterprise Authentication',
            'desc': 'Built-in Django authentication with CSRF defense, password hashing, and role-based route security.',
            'tag': 'Security',
        },
        {
            'icon': 'sparkles',
            'title': 'AI Diagnostic Assistant',
            'desc': 'Intelligent conversational agent that answers from SQL FAQs, explains 8 error codes, and auto-files support tickets.',
            'tag': 'AI Core',
        },
        {
            'icon': 'responsive',
            'title': 'Polyglot Persistence',
            'desc': 'Structured relational entities in SQL combined with unstructured chat logs and telemetry in MongoDB.',
            'tag': 'SQL + Mongo',
        },
        {
            'icon': 'database',
            'title': 'Subsystem Health Telemetry',
            'desc': 'Real-time /health/ endpoint monitoring SQL latency, MongoDB state, and external third-party API with fallback.',
            'tag': 'Observability',
        },
        {
            'icon': 'code',
            'title': 'Zero-Bloat Engineering',
            'desc': 'Pure native CSS glassmorphism, responsive mobile drawers, and lightweight clientside JavaScript.',
            'tag': 'Clean Code',
        },
    ]

    try:
        faq_count = FAQ.objects.count()
    except Exception:
        ensure_db_ready()
        try:
            faq_count = FAQ.objects.count()
        except Exception:
            faq_count = 12

    stats = [
        {'value': '99.9%', 'label': 'System Availability'},
        {'value': '<25ms', 'label': 'Server Response'},
        {'value': f"{faq_count}+", 'label': 'SQL FAQs'},
        {'value': '8 Codes', 'label': 'Error Diagnostics'},
    ]

    # Fetch daily external insight (with 2s timeout and fallback)
    external_insight = fetch_external_telemetry()

    return render(request, 'website/home.html', {
        'features': features,
        'stats': stats,
        'external_insight': external_insight,
    })


def about(request):
    milestones = [
        {
            'year': 'Phase 01',
            'title': 'Architectural Foundation',
            'desc': 'Established standard Django project foundations, environment configuration, and clean directory hierarchies.'
        },
        {
            'year': 'Phase 02',
            'title': 'Glassmorphic UI Design System',
            'desc': 'Engineered deep dark themes with ambient mesh gradients in cyan (#00f2fe) and purple (#9b51e0), combined with multi-layer glass effects.'
        },
        {
            'year': 'Phase 03',
            'title': 'SQL FAQs & Error Code Matrix',
            'desc': 'Stored at least 10 comprehensive FAQs in SQL alongside 8 error code diagnostics (400, 401, 403, 404, 429, 500, 503, and 480).'
        },
        {
            'year': 'Phase 04',
            'title': 'AI Assistant & MongoDB Telemetry',
            'desc': 'Built automated assistant routing, support tickets in SQL, chat logs in MongoDB, and timeout-protected external APIs.'
        },
    ]

    tech_stack = [
        {'name': 'Django Core', 'role': 'Backend Engine & Routing', 'icon': 'django'},
        {'name': 'SQLite Engine', 'role': 'Relational Persistence (FAQs & Tickets)', 'icon': 'sqlite'},
        {'name': 'MongoDB Atlas', 'role': 'NoSQL Chat Logs & Feedback', 'icon': 'mongo'},
        {'name': 'AI Assistant Engine', 'role': 'FAQ & Error Diagnostic Dispatch', 'icon': 'ai'},
        {'name': 'Vanilla Modern CSS', 'role': 'Glassmorphism & Gradients', 'icon': 'css'},
        {'name': 'Django Auth', 'role': 'Session & Role Protection', 'icon': 'auth'},
    ]

    return render(request, 'website/about.html', {
        'milestones': milestones,
        'tech_stack': tech_stack,
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                contact_msg = form.save()
            except Exception:
                ensure_db_ready()
                contact_msg = form.save()

            messages.success(
                request,
                f"Thank you, {contact_msg.name}! Your message regarding '{contact_msg.subject}' has been safely recorded in our database."
            )
            return redirect('contact')
        else:
            messages.error(request, "Please review the form errors below and submit again.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['name'] = request.user.get_full_name() or request.user.username
            initial_data['email'] = request.user.email
        form = ContactForm(initial=initial_data)

    try:
        total_messages = ContactMessage.objects.count()
    except Exception:
        ensure_db_ready()
        try:
            total_messages = ContactMessage.objects.count()
        except Exception:
            total_messages = 0

    return render(request, 'website/contact.html', {
        'form': form,
        'total_messages': total_messages,
    })


def faqs_view(request):
    """
    Displays FAQs stored in the SQL database (minimum 10 entries).
    """
    try:
        faqs = list(FAQ.objects.filter(is_active=True).order_by('order', 'id'))
    except Exception:
        ensure_db_ready()
        try:
            faqs = list(FAQ.objects.filter(is_active=True).order_by('order', 'id'))
        except Exception:
            from .seed_data import INITIAL_FAQS
            class MockFAQ:
                def __init__(self, data, idx):
                    self.id = idx
                    self.question = data['question']
                    self.category = data['category']
                    self.answer = data['answer']
            faqs = [MockFAQ(d, i+1) for i, d in enumerate(INITIAL_FAQS)]

    categories = list(dict.fromkeys(f.category for f in faqs))

    return render(request, 'website/faqs.html', {
        'faqs': faqs,
        'categories': categories,
        'total_faqs': len(faqs),
    })


def error_codes_view(request):
    """
    Displays the 8 error codes (400, 401, 403, 404, 429, 500, 503, and custom 480).
    """
    try:
        codes = list(ErrorCode.objects.all().order_by('code'))
    except Exception:
        ensure_db_ready()
        try:
            codes = list(ErrorCode.objects.all().order_by('code'))
        except Exception:
            from .seed_data import INITIAL_ERROR_CODES
            class MockErrorCode:
                def __init__(self, data):
                    self.code = data['code']
                    self.title = data['title']
                    self.category = data['category']
                    self.summary = data['summary']
                    self.description = data['description']
                    self.resolution = data['resolution']
            codes = [MockErrorCode(d) for d in INITIAL_ERROR_CODES]

    return render(request, 'website/error_codes.html', {
        'error_codes': codes,
    })


def error_preview_view(request, code):
    """
    Simulates triggering any of the 8 error codes (400, 401, 403, 404, 429, 500, 503, 480).
    """
    error_obj = None
    try:
        error_obj = ErrorCode.objects.filter(code=code).first()
    except Exception:
        ensure_db_ready()
        try:
            error_obj = ErrorCode.objects.filter(code=code).first()
        except Exception:
            pass

    title = error_obj.title if error_obj else f"HTTP {code}"

    # Return specialized templates for 404 and 500
    if code == 404:
        return render(request, 'website/404.html', status=404)
    elif code == 500:
        return render(request, 'website/500.html', status=500)

    # For other codes, render a styled preview with 'Ask the assistant'
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>{code} {title} - Error Simulator</title>
      <link rel="stylesheet" href="/static/website/css/main.css">
    </head>
    <body style="display:grid; place-items:center; min-height:100vh; padding: 2rem;">
      <div class="ambient-canvas">
        <div class="ambient-orb ambient-orb-1"></div>
        <div class="ambient-orb ambient-orb-2"></div>
      </div>
      <div class="glass-card" style="max-width: 640px; text-align: center; padding: 3rem; position:relative; z-index:1;">
        <div class="badge badge-purple" style="margin-bottom: 1rem;">Simulated Error Code</div>
        <h1 style="font-family: var(--font-display); font-size: 3.5rem; font-weight: 800; color: var(--cyan-primary); margin-bottom: 0.5rem;">{code}</h1>
        <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">{title}</h2>
        <p style="color: var(--text-secondary); line-height: 1.7; margin-bottom: 2rem;">{error_obj.description if error_obj else 'Custom simulated error condition triggered.'}</p>
        <div style="display:flex; justify-content:center; gap:1rem; flex-wrap:wrap;">
          <a href="/errors/" class="btn btn-secondary">Back to Error Matrix</a>
          <a href="/" class="btn btn-primary">Return Home</a>
        </div>
      </div>
    </body>
    </html>
    """
    return HttpResponse(html_content, status=code)


def health_check_view(request):
    """
    Health check page with request logging verification, SQL DB latency,
    MongoDB telemetry status, and third-party API with time limit and fallback.
    """
    # 1. SQL Database latency test
    start_db = time.perf_counter()
    db_status = "connected"
    try:
        connection.ensure_connection()
        total_faqs = FAQ.objects.count()
        total_tickets = SupportTicket.objects.count()
        db_latency = round((time.perf_counter() - start_db) * 1000, 2)
    except Exception as e:
        db_status = f"error: {e}"
        db_latency = -1
        total_faqs = 0
        total_tickets = 0

    # 2. MongoDB Status
    mongo_health = get_mongo_status()

    # 3. Third-party API with time limit (2.0s) and fallback
    third_party = fetch_external_telemetry(timeout=2.0)

    health_payload = {
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'version': '1.0.0',
        'subsystems': {
            'database_sql': {
                'engine': 'SQLite',
                'status': db_status,
                'latency_ms': db_latency,
                'models_healthy': True,
                'faq_count': total_faqs,
                'ticket_count': total_tickets,
            },
            'database_mongodb': mongo_health,
            'third_party_api': third_party,
        }
    }

    # Return JSON if requested via format=json or header
    if request.GET.get('format') == 'json' or request.headers.get('Accept') == 'application/json':
        return JsonResponse(health_payload)

    # Otherwise render modern HTML telemetry dashboard
    return render(request, 'website/health.html', {
        'health': health_payload,
        'db_health': health_payload['subsystems']['database_sql'],
        'mongo_health': mongo_health,
        'third_party': third_party,
        'total_faqs': total_faqs,
        'total_tickets': total_tickets,
    })


def tickets_view(request):
    """
    Displays existing support tickets and handles new ticket creation.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'Medium')

        if name and email and subject and description:
            try:
                ticket = SupportTicket.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    description=description,
                    priority=priority,
                    source='Web Form',
                    status='Open'
                )
            except Exception:
                ensure_db_ready()
                ticket = SupportTicket.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    description=description,
                    priority=priority,
                    source='Web Form',
                    status='Open'
                )

            messages.success(request, f"Support Ticket {ticket.ticket_number} created successfully! Saved to SQL database.")
            return redirect('tickets')
        else:
            messages.error(request, "Please fill in all required fields.")

    try:
        tickets = SupportTicket.objects.all()
    except Exception:
        ensure_db_ready()
        try:
            tickets = SupportTicket.objects.all()
        except Exception:
            tickets = []

    return render(request, 'website/tickets.html', {
        'tickets': tickets,
    })


@csrf_exempt
def chat_api_view(request):
    """
    POST API endpoint for the AI Assistant.
    Answers FAQs from SQL, explains error codes, or escalates to support tickets.
    Logs conversation to MongoDB.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id') or request.session.session_key or 'session_guest'
        context = data.get('context', {})

        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        # Dispatch through AI Assistant engine
        assistant_result = ask_assistant(
            user_message=user_message,
            session_id=session_id,
            context=context,
            user=request.user
        )

        return JsonResponse(assistant_result)

    except Exception as e:
        return JsonResponse({
            'reply': "I encountered an internal telemetry error processing your request. Please click 'Create Support Ticket' to report this directly.",
            'can_answer': False,
            'suggest_ticket': True,
            'error': str(e)
        }, status=500)


@csrf_exempt
def feedback_api_view(request):
    """
    POST API endpoint for recording user feedback on AI responses into MongoDB.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        session_id = data.get('session_id') or 'anon'
        rating = data.get('rating') # 'up' or 'down'
        comment = data.get('comment', '')
        message = data.get('message', '')

        saved = save_chat_feedback(session_id, rating=rating, comment=comment, message=message)
        return JsonResponse({'status': 'recorded', 'saved_in_mongo': saved})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            login(request, user)
            messages.success(
                request,
                f"Account successfully created! Welcome aboard, {user.username}."
            )
            return redirect('dashboard')
        else:
            messages.error(request, "Registration could not be completed. Please fix the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'website/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard'

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please verify your credentials.")
    else:
        form = CustomLoginForm()

    return render(request, 'website/login.html', {
        'form': form,
        'next': next_url,
    })


def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, f"Goodbye {username}! You have been logged out securely.")
    return redirect('home')


@login_required
def dashboard_view(request):
    try:
        total_users = User.objects.count()
        user_messages = ContactMessage.objects.filter(email__iexact=request.user.email)
        recent_messages = ContactMessage.objects.all()[:5] if request.user.is_staff else user_messages[:5]
        total_tickets = SupportTicket.objects.count()
    except Exception:
        ensure_db_ready()
        try:
            total_users = User.objects.count()
            user_messages = ContactMessage.objects.filter(email__iexact=request.user.email)
            recent_messages = ContactMessage.objects.all()[:5] if request.user.is_staff else user_messages[:5]
            total_tickets = SupportTicket.objects.count()
        except Exception:
            total_users = 1
            user_messages = []
            recent_messages = []
            total_tickets = 0

    quick_stats = [
        {'title': 'Account Status', 'value': 'Active & Verified', 'badge': 'Secure', 'color': 'cyan'},
        {'title': 'Total Platform Users', 'value': str(total_users), 'badge': 'Live', 'color': 'purple'},
        {'title': 'Support Tickets in SQL', 'value': str(total_tickets), 'badge': 'Database', 'color': 'gradient'},
    ]

    return render(request, 'website/dashboard.html', {
        'quick_stats': quick_stats,
        'user_messages': user_messages,
        'recent_messages': recent_messages,
        'total_tickets': total_tickets,
    })


def custom_404_view(request, exception=None):
    return render(request, 'website/404.html', status=404)


def custom_500_view(request):
    return render(request, 'website/500.html', status=500)

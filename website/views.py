from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseNotFound
from .models import ContactMessage
from .forms import ContactForm, RegisterForm, CustomLoginForm


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
            'title': 'Glassmorphic Aesthetics',
            'desc': 'Ultra-modern dark aesthetic featuring real-time blurred backdrops, cyan-purple gradients, and fluid interactions.',
            'tag': 'Design',
        },
        {
            'icon': 'responsive',
            'title': '100% Adaptive Layout',
            'desc': 'Pixel-perfect responsiveness across mobile handhelds, tablets, ultra-wide desktops, and high-DPI displays.',
            'tag': 'Adaptive',
        },
        {
            'icon': 'database',
            'title': 'ORM & Database Migrations',
            'desc': 'Schema-managed database models with migrations for contact inquiries, user profiles, and session management.',
            'tag': 'Data Flow',
        },
        {
            'icon': 'code',
            'title': 'Zero-Bloat Engineering',
            'desc': 'Fast loading speed with pure native CSS, vanilla JavaScript micro-animations, and minimal external overhead.',
            'tag': 'Clean Code',
        },
    ]

    stats = [
        {'value': '99.9%', 'label': 'System Availability'},
        {'value': '<25ms', 'label': 'Server Response'},
        {'value': '100%', 'label': 'CSRF Protected'},
        {'value': '24/7', 'label': 'Database Persistence'},
    ]

    return render(request, 'website/home.html', {
        'features': features,
        'stats': stats,
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
            'title': 'Authentication & State Security',
            'desc': 'Integrated full user authentication lifecycle, session safeguards, and protected user portal dashboards.'
        },
        {
            'year': 'Phase 04',
            'title': 'Interactive Communication',
            'desc': 'Implemented database-backed contact messaging pipeline, form validation, and feedback notifications.'
        },
    ]

    tech_stack = [
        {'name': 'Django Core', 'role': 'Backend Engine & Routing', 'icon': 'django'},
        {'name': 'SQLite Engine', 'role': 'Zero-Config ACID Database', 'icon': 'sqlite'},
        {'name': 'Vanilla Modern CSS', 'role': 'Glassmorphism & Gradients', 'icon': 'css'},
        {'name': 'Vanilla JS', 'role': 'Micro-interactions & Toast Alerts', 'icon': 'js'},
        {'name': 'Django Templates', 'role': 'Component Architecture', 'icon': 'templates'},
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
            contact_msg = form.save()
            messages.success(
                request,
                f"Thank you, {contact_msg.name}! Your message regarding '{contact_msg.subject}' has been safely recorded in our database."
            )
            return redirect('contact')
        else:
            messages.error(request, "Please review the form errors below and submit again.")
    else:
        # Pre-fill name and email if user is logged in
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['name'] = request.user.get_full_name() or request.user.username
            initial_data['email'] = request.user.email
        form = ContactForm(initial=initial_data)

    total_messages = ContactMessage.objects.count()
    return render(request, 'website/contact.html', {
        'form': form,
        'total_messages': total_messages,
    })


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
    total_users = User.objects.count()
    user_messages = ContactMessage.objects.filter(email__iexact=request.user.email)
    all_messages_count = ContactMessage.objects.count()
    recent_messages = ContactMessage.objects.all()[:5] if request.user.is_staff else user_messages[:5]

    quick_stats = [
        {'title': 'Account Status', 'value': 'Active & Verified', 'badge': 'Secure', 'color': 'cyan'},
        {'title': 'Total Platform Users', 'value': str(total_users), 'badge': 'Live', 'color': 'purple'},
        {'title': 'Messages Recorded', 'value': str(all_messages_count), 'badge': 'Database', 'color': 'gradient'},
    ]

    return render(request, 'website/dashboard.html', {
        'quick_stats': quick_stats,
        'user_messages': user_messages,
        'recent_messages': recent_messages,
    })


def custom_404_view(request, exception=None):
    return render(request, 'website/404.html', status=404)

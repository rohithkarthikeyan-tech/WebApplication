from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faqs/', views.faqs_view, name='faqs'),
    path('errors/', views.error_codes_view, name='error_codes'),
    path('error-preview/<int:code>/', views.error_preview_view, name='error_preview'),
    path('health/', views.health_check_view, name='health_check'),
    path('tickets/', views.tickets_view, name='tickets'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('404/', views.custom_404_view, name='custom_404'),
    path('500/', views.custom_500_view, name='custom_500'),
    # AI Assistant & MongoDB Endpoints
    path('api/chat/', views.chat_api_view, name='chat_api'),
    path('api/feedback/', views.feedback_api_view, name='feedback_api'),
]

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import ContactMessage


class WebsiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testpilot'
        self.email = 'pilot@example.com'
        self.password = 'ComplexPass123!'
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def test_home_page_status_and_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/home.html')
        self.assertTemplateUsed(response, 'website/base.html')
        self.assertContains(response, 'Aether')
        self.assertContains(response, 'Django 6.1')

    def test_about_page_status_and_template(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/about.html')
        self.assertContains(response, 'Architectural Roadmap')
        self.assertContains(response, 'about_architecture.jpg')

    def test_contact_page_get(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/contact.html')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contact_form_submission_saves_to_db(self):
        initial_count = ContactMessage.objects.count()
        payload = {
            'name': 'Ada Lovelace',
            'email': 'ada@analyticalengine.org',
            'subject': 'Algorithm Pipeline Inquiry',
            'message': 'Testing message persistence directly in SQLite.'
        }
        response = self.client.post(reverse('contact'), payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), initial_count + 1)
        saved = ContactMessage.objects.latest('created_at')
        self.assertEqual(saved.name, 'Ada Lovelace')
        self.assertEqual(saved.subject, 'Algorithm Pipeline Inquiry')
        self.assertContains(response, 'Your message regarding')

    def test_registration_view_creates_user_and_authenticates(self):
        payload = {
            'username': 'novadev',
            'email': 'nova@example.com',
            'password': 'SecureP@ssword2026',
            'password_confirm': 'SecureP@ssword2026',
        }
        response = self.client.post(reverse('register'), payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='novadev').exists())
        self.assertContains(response, 'novadev')
        self.assertTemplateUsed(response, 'website/dashboard.html')

    def test_registration_passwords_mismatch(self):
        payload = {
            'username': 'mismatchuser',
            'email': 'mismatch@example.com',
            'password': 'Password123!',
            'password_confirm': 'DifferentPassword456!',
        }
        response = self.client.post(reverse('register'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatchuser').exists())
        self.assertContains(response, 'Passwords do not match')

    def test_login_and_logout_flow(self):
        # Successful login
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/dashboard.html')
        self.assertContains(response, self.username)

        # Logout
        logout_response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(logout_response.status_code, 200)
        self.assertTemplateUsed(logout_response, 'website/home.html')

    def test_dashboard_is_protected(self):
        # Anonymous user redirected to login
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

        # Logged in user can access dashboard
        self.client.login(username=self.username, password=self.password)
        auth_response = self.client.get(reverse('dashboard'))
        self.assertEqual(auth_response.status_code, 200)
        self.assertTemplateUsed(auth_response, 'website/dashboard.html')
        self.assertContains(auth_response, self.username)

    def test_custom_404_page(self):
        response = self.client.get(reverse('custom_404'))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'website/404.html')
        self.assertContains(response, '404', status_code=404)
        self.assertContains(response, 'Coordinates Unreachable', status_code=404)

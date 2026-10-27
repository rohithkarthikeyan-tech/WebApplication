import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import ContactMessage, FAQ, ErrorCode, SupportTicket
from .services import fetch_external_telemetry


class WebsiteExtendedTests(TestCase):
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

    def test_faq_database_has_minimum_10_entries(self):
        """Verifies requirement: minimum of 10 FAQs stored in SQL database"""
        count = FAQ.objects.filter(is_active=True).count()
        self.assertGreaterEqual(count, 10, f"Expected at least 10 FAQs in SQL DB, found {count}")

    def test_faq_page_renders_with_faqs(self):
        """Verifies FAQ page renders with FAQs and search input"""
        response = self.client.get(reverse('faqs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/faqs.html')
        self.assertContains(response, 'Frequently Asked Questions')
        self.assertContains(response, 'faq-search-input')
        self.assertContains(response, 'What is Aether and how is it architected?')

    def test_error_codes_has_minimum_8_entries(self):
        """Verifies requirement: minimum of 8 error codes (400, 401, 403, 404, 429, 500, 503, and custom 480)"""
        required_codes = [400, 401, 403, 404, 429, 500, 503, 480]
        db_codes = list(ErrorCode.objects.values_list('code', flat=True))
        for code in required_codes:
            self.assertIn(code, db_codes, f"Required error code {code} missing from SQL database")

    def test_error_codes_directory_page(self):
        """Verifies error codes page renders all 8 codes"""
        response = self.client.get(reverse('error_codes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/error_codes.html')
        self.assertContains(response, 'HTTP 400')
        self.assertContains(response, 'HTTP 404')
        self.assertContains(response, 'HTTP 500')
        self.assertContains(response, 'HTTP 480')
        self.assertContains(response, 'Aether Quantum Sync Failure')

    def test_custom_404_page_has_ask_assistant(self):
        """Verifies custom 404 page has Ask the assistant option"""
        response = self.client.get(reverse('custom_404'))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'website/404.html')
        self.assertContains(response, 'Ask the Assistant', status_code=404)
        self.assertContains(response, 'openAssistantWithError(404', status_code=404)

    def test_custom_500_page_has_ask_assistant(self):
        """Verifies custom 500 page has Ask the assistant option"""
        response = self.client.get(reverse('custom_500'))
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, 'website/500.html')
        self.assertContains(response, 'Ask the Assistant', status_code=500)
        self.assertContains(response, 'openAssistantWithError(500', status_code=500)

    def test_site_specific_error_preview_480(self):
        """Verifies triggering site-specific error code 480"""
        response = self.client.get(reverse('error_preview', kwargs={'code': 480}))
        self.assertEqual(response.status_code, 480)
        self.assertContains(response, '480', status_code=480)
        self.assertContains(response, 'Aether Quantum Sync Failure', status_code=480)

    def test_ai_assistant_answers_from_sql_faq(self):
        """Verifies AI assistant answers from SQL FAQ data"""
        payload = {
            'message': 'What is Aether and how is it architected?',
            'session_id': 'test_sess_01'
        }
        response = self.client.post(
            reverse('chat_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['can_answer'])
        self.assertIn('Aether', data['reply'])
        self.assertIn('SQL FAQ Database', data['reply'])

    def test_ai_assistant_explains_error_codes(self):
        """Verifies AI assistant explains error code 480 and 404"""
        payload = {
            'message': 'Can you explain error 480?',
            'session_id': 'test_sess_02'
        }
        response = self.client.post(
            reverse('chat_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['intent'], 'error_explanation')
        self.assertIn('480', data['reply'])
        self.assertIn('Quantum Sync', data['reply'])

    def test_ai_assistant_escalates_when_cannot_answer(self):
        """Verifies AI assistant offers support ticket when it cannot answer"""
        payload = {
            'message': 'xyz999unrelatednonsensequerythatmatchesnofaq',
            'session_id': 'test_sess_03'
        }
        response = self.client.post(
            reverse('chat_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['can_answer'])
        self.assertTrue(data['suggest_ticket'])
        self.assertIn('create a Support Ticket', data['reply'])

    def test_ai_assistant_creates_support_ticket_in_sql(self):
        """Verifies support ticket creation via assistant is stored in SQL"""
        initial_count = SupportTicket.objects.count()
        payload = {
            'message': 'Please create ticket: Database latency spike on node 3',
            'session_id': 'test_sess_04'
        }
        response = self.client.post(
            reverse('chat_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SupportTicket.objects.count(), initial_count + 1)
        latest_ticket = SupportTicket.objects.latest('created_at')
        self.assertTrue(latest_ticket.ticket_number.startswith('TICK-'))
        self.assertEqual(latest_ticket.source, 'AI Assistant')

    def test_feedback_api_records(self):
        """Verifies feedback API returns success"""
        payload = {
            'session_id': 'test_sess_05',
            'rating': 'up',
            'message': 'Great explanation of error 404'
        }
        response = self.client.post(
            reverse('feedback_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'recorded')

    def test_health_check_json_endpoint(self):
        """Verifies health check endpoint returns JSON with SQL DB and third-party API telemetry"""
        response = self.client.get(reverse('health_check'), {'format': 'json'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('database_sql', data['subsystems'])
        self.assertEqual(data['subsystems']['database_sql']['status'], 'connected')
        self.assertIn('database_mongodb', data['subsystems'])
        self.assertIn('third_party_api', data['subsystems'])
        self.assertIn('timeout_threshold_seconds', data['subsystems']['third_party_api'])

    def test_third_party_api_service_with_timeout_and_fallback(self):
        """Verifies third-party API enforces timeout and provides fallback data"""
        telemetry = fetch_external_telemetry(timeout=2.0)
        self.assertIn(telemetry['status'], ['online', 'fallback'])
        self.assertIn('quote', telemetry['data'])
        self.assertIn('author', telemetry['data'])
        self.assertEqual(telemetry['timeout_threshold_seconds'], 2.0)

    def test_tickets_page_and_form_submission(self):
        """Verifies support tickets web page and SQL form submission"""
        initial_count = SupportTicket.objects.count()
        response = self.client.post(reverse('tickets'), {
            'name': 'Grace Hopper',
            'email': 'grace@compiler.org',
            'subject': 'Syntax Parser Malfunction',
            'description': 'Found a moth inside relay #70.',
            'priority': 'High'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SupportTicket.objects.count(), initial_count + 1)
        ticket = SupportTicket.objects.latest('created_at')
        self.assertEqual(ticket.name, 'Grace Hopper')
        self.assertEqual(ticket.priority, 'High')

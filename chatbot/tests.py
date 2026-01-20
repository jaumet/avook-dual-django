from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock
from chatbot.models import ChatSession, ChatMessage
from chatbot.views import chat_api
import json

class ChatAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='testuser', password='password')

    @patch('chatbot.views.get_openai_response')
    def test_chat_api_success(self, mock_get_openai_response):
        mock_get_openai_response.return_value = "This is a test response."

        request = self.factory.post(
            '/api/chat/',
            data=json.dumps({'message': 'Hello'}),
            content_type='application/json'
        )
        request.user = self.user

        response = chat_api(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'reply': 'This is a test response.'})

        self.assertTrue(ChatSession.objects.filter(user=self.user).exists())
        session = ChatSession.objects.get(user=self.user)

        self.assertTrue(ChatMessage.objects.filter(session=session, role='user', content='Hello').exists())
        self.assertTrue(ChatMessage.objects.filter(session=session, role='assistant', content='This is a test response.').exists())

    @patch('chatbot.views.get_openai_response')
    def test_chat_session_creation(self, mock_get_openai_response):
        mock_get_openai_response.return_value = "Response"

        # First request, should create a session
        request1 = self.factory.post('/api/chat/', data=json.dumps({'message': 'Message 1'}), content_type='application/json')
        request1.user = self.user
        chat_api(request1)
        self.assertEqual(ChatSession.objects.filter(user=self.user).count(), 1)

        # Second request immediately after, should use the same session
        request2 = self.factory.post('/api/chat/', data=json.dumps({'message': 'Message 2'}), content_type='application/json')
        request2.user = self.user
        chat_api(request2)
        self.assertEqual(ChatSession.objects.filter(user=self.user).count(), 1)

        # Manually move all messages in the session back in time to simulate inactivity
        session = ChatSession.objects.get(user=self.user)
        session.messages.all().update(created_at=timezone.now() - timezone.timedelta(hours=2))

        # Third request after a simulated delay, should create a new session
        request3 = self.factory.post('/api/chat/', data=json.dumps({'message': 'Message 3'}), content_type='application/json')
        request3.user = self.user
        chat_api(request3)
        self.assertEqual(ChatSession.objects.filter(user=self.user).count(), 2)

    def test_chat_api_missing_message(self):
        request = self.factory.post(
            '/api/chat/',
            data=json.dumps({}),
            content_type='application/json'
        )
        request.user = self.user

        response = chat_api(request)

        self.assertEqual(response.status_code, 400)

    @patch('chatbot.views.CHATBOT_MAX_MESSAGES_PER_DAY', 1)
    def test_chat_api_rate_limit(self):
        # First message should succeed
        with patch('chatbot.views.get_openai_response') as mock_get_openai_response:
            mock_get_openai_response.return_value = "Response 1"
            request1 = self.factory.post('/api/chat/', data=json.dumps({'message': 'Message 1'}), content_type='application/json')
            request1.user = self.user
            response1 = chat_api(request1)
            self.assertEqual(response1.status_code, 200)

        # Second message should fail
        with patch('chatbot.views.get_openai_response') as mock_get_openai_response:
            mock_get_openai_response.return_value = "Response 2"
            request2 = self.factory.post('/api/chat/', data=json.dumps({'message': 'Message 2'}), content_type='application/json')
            request2.user = self.user
            response2 = chat_api(request2)
            self.assertEqual(response2.status_code, 403)

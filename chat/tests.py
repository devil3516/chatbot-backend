from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from chat.utils.ai_chat import chat_with_groq
import json
from unittest.mock import patch
import os

# Create your tests here.

class ChatViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.chat_url = reverse('chat:chat')
        self.api_url = reverse('chat:groq_chat')
        
        # Mock environment variable for tests
        os.environ['GROQ_API_KEY'] = 'test_api_key'

    def test_chat_view_GET(self):
        """Test that chat page renders correctly"""
        response = self.client.get(self.chat_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat.html')
        self.assertContains(response, 'AI Assistant')

    @patch('chat.utils.ai_chat.Groq')
    def test_groq_chat_view_success(self, mock_groq):
        """Test successful API request to Groq"""
        # Setup mock response
        mock_response = {
            "choices": [{
                "message": {
                    "content": "Test response from AI",
                    "role": "assistant"
                }
            }]
        }
        mock_groq.return_value.chat.completions.create.return_value = mock_response

        # Make request
        response = self.client.post(
            self.api_url,
            data=json.dumps({'message': 'Test message'}),
            content_type='application/json'
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'response': 'Test response from AI'
        })

    def test_groq_chat_view_invalid_method(self):
        """Test GET request to API endpoint (should fail)"""
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, 405)

    def test_groq_chat_view_missing_message(self):
        """Test request with missing message parameter"""
        response = self.client.post(
            self.api_url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', json.loads(response.content))

    @patch('chat.utils.ai_chat.Groq')
    def test_groq_chat_view_api_error(self, mock_groq):
        """Test error handling when Groq API fails"""
        mock_groq.return_value.chat.completions.create.side_effect = Exception("API Error")

        response = self.client.post(
            self.api_url,
            data=json.dumps({'message': 'Test message'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn('error', json.loads(response.content))


class GroqUtilityTests(TestCase):
    @patch('chat.utils.ai_chat.Groq')
    def test_chat_with_groq_success(self, mock_groq):
        """Test successful chat_with_groq function"""
        # Setup mock
        mock_response = {
            "choices": [{
                "message": {
                    "content": "Test response",
                    "role": "assistant"
                }
            }]
        }
        mock_groq.return_value.chat.completions.create.return_value = mock_response

        # Call function
        response = chat_with_groq("Test message")

        # Verify
        self.assertEqual(response, "Test response")
        mock_groq.return_value.chat.completions.create.assert_called_once()

    @patch('chat.utils.ai_chat.Groq')
    def test_chat_with_groq_empty_message(self, mock_groq):
        """Test with empty message"""
        with self.assertRaises(ValueError):
            chat_with_groq("")

    @patch('chat.utils.ai_chat.Groq')
    def test_chat_with_groq_api_error(self, mock_groq):
        """Test error handling in chat_with_groq"""
        mock_groq.return_value.chat.completions.create.side_effect = Exception("API Error")

        with self.assertRaises(Exception):
            chat_with_groq("Test message")


class StaticFilesTests(TestCase):
    def test_css_file_exists(self):
        """Test that CSS file is properly served"""
        response = self.client.get('/static/chat/css/chat.css')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/css')

    def test_js_file_exists(self):
        """Test that JS file is properly served"""
        response = self.client.get('/static/chat/js/chat.js')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/javascript')

from django.test import TestCase, override_settings
from django.utils import translation
from unittest.mock import patch
from .models import EmailTemplate, EmailTemplateTranslation
from .utils import send_templated_email

class TestSendTemplatedEmail(TestCase):

    @classmethod
    def setUpTestData(cls):
        template = EmailTemplate.objects.create(name='test_template')
        EmailTemplateTranslation.objects.create(
            template=template,
            language='ca',
            subject='Hola {{ name }}',
            body='Això és una prova.'
        )
        EmailTemplateTranslation.objects.create(
            template=template,
            language='en',
            subject='Hello {{ name }}',
            body='This is a test.'
        )
        EmailTemplateTranslation.objects.create(
            template=template,
            language='es',
            subject='Hola {{ name }}',
            body='Esto es una prueba.'
        )

    @patch('post_office.utils.send_mail')
    def test_sends_email_in_correct_language(self, mock_send_mail):
        """Test that the email is sent in the activated language."""
        context = {'name': 'Jules'}
        with translation.override('es'):
            send_templated_email('test_template', context, 'test@example.com')

        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        self.assertEqual(args[0], 'Hola Jules')
        self.assertEqual(args[1], 'Esto es una prueba.')
        self.assertEqual(args[3], ['test@example.com'])
        self.assertEqual(kwargs['html_message'], 'Esto es una prueba.')

    @patch('post_office.utils.send_mail')
    @override_settings(LANGUAGE_CODE='en')
    def test_falls_back_to_default_language(self, mock_send_mail):
        """Test that it falls back to the default language if the active one is not available."""
        context = {'name': 'Jules'}
        # 'fr' is not a defined translation for the template
        with translation.override('fr'):
            send_templated_email('test_template', context, 'test@example.com')

        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        self.assertEqual(args[0], 'Hello Jules')
        self.assertEqual(args[1], 'This is a test.')

    @patch('post_office.utils.send_mail')
    def test_handles_regional_language_code(self, mock_send_mail):
        """Test that a regional language code like 'en-GB' correctly uses the base 'en' template."""
        context = {'name': 'Jules'}
        with translation.override('en-GB'):
            send_templated_email('test_template', context, 'test@example.com')

        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        self.assertEqual(args[0], 'Hello Jules')
        self.assertEqual(args[1], 'This is a test.')

    @patch('post_office.utils.send_mail')
    def test_logs_error_if_template_not_found(self, mock_send_mail):
        """Test that an error is logged if the email template does not exist."""
        with self.assertLogs('post_office.utils', level='ERROR') as cm:
            send_templated_email('nonexistent_template', {}, 'test@example.com')
            self.assertEqual(len(cm.output), 1)
            self.assertIn("Email template 'nonexistent_template' not found.", cm.output[0])

        mock_send_mail.assert_not_called()

    @patch('post_office.utils.send_mail')
    def test_logs_error_if_no_translations_found(self, mock_send_mail):
        """Test that an error is logged if no translations exist for a template."""
        EmailTemplate.objects.create(name='no_translations')
        with self.assertLogs('post_office.utils', level='ERROR') as cm:
            send_templated_email('no_translations', {}, 'test@example.com')
            self.assertEqual(len(cm.output), 1)
            self.assertIn("No translations found for email template 'no_translations'.", cm.output[0])

        mock_send_mail.assert_not_called()

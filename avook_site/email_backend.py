import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMessage
from django.conf import settings

class ResendEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0
        api_key = settings.RESEND_API_KEY
        url = "https://api.resend.com/emails"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        for message in email_messages:
            data = {
                "from": message.from_email,
                "to": message.to,
                "subject": message.subject,
                "html": message.body,
            }

            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                sent_count += 1
            else:
                print("Resend error:", response.text)

        return sent_count


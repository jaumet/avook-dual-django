import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY

def send_email(
    *,
    to: list[str],
    subject: str,
    html: str,
    text: str | None = None,
):
    """
    Envia un email via Resend API (HTTP).
    """
    return resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": to,
        "subject": subject,
        "html": html,
        "text": text,
    })

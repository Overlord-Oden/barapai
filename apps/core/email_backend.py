"""
Backend email custom utilisant l'API HTTP Resend.
Utilise requests (déjà installé) — contourne le blocage SMTP sur Railway.
"""
import logging

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

RESEND_API_URL = 'https://api.resend.com/emails'


class ResendEmailBackend(BaseEmailBackend):
    """Envoie les emails via l'API REST Resend (port 443, jamais bloqué)."""

    def send_messages(self, email_messages):
        api_key = getattr(settings, 'RESEND_API_KEY', '')
        if not api_key:
            logger.error('RESEND_API_KEY non configuré — email non envoyé')
            return 0

        sent = 0
        for message in email_messages:
            from_email = message.from_email or settings.DEFAULT_FROM_EMAIL

            payload = {
                'from': from_email,
                'to': list(message.to),
                'subject': message.subject,
                'text': message.body,
            }

            try:
                response = requests.post(
                    RESEND_API_URL,
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json',
                    },
                    json=payload,
                    timeout=10,
                )
                response.raise_for_status()
                sent += 1
            except requests.HTTPError as exc:
                logger.error('Resend API HTTP error: %s — %s', exc, response.text)
                if not self.fail_silently:
                    raise
            except Exception as exc:
                logger.error('Resend API error: %s', exc)
                if not self.fail_silently:
                    raise

        return sent

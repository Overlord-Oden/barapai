"""
Backend email custom utilisant l'API HTTP SendGrid.
Utilise requests (déjà installé) — contourne le blocage SMTP sur Railway.
"""
import logging

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

SENDGRID_API_URL = 'https://api.sendgrid.com/v3/mail/send'


class SendGridEmailBackend(BaseEmailBackend):
    """Envoie les emails via l'API REST SendGrid (port 443, jamais bloqué)."""

    def send_messages(self, email_messages):
        api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        if not api_key:
            logger.error('SENDGRID_API_KEY non configuré — email non envoyé')
            return 0

        sent = 0
        for message in email_messages:
            from_email = message.from_email or settings.DEFAULT_FROM_EMAIL
            if '<' in from_email:
                name, addr = from_email.split('<', 1)
                from_obj = {'name': name.strip(), 'email': addr.rstrip('>')}
            else:
                from_obj = {'email': from_email, 'name': 'Barapai'}

            payload = {
                'personalizations': [
                    {'to': [{'email': addr} for addr in message.to]}
                ],
                'from': from_obj,
                'subject': message.subject,
                'content': [{'type': 'text/plain', 'value': message.body}],
            }

            try:
                response = requests.post(
                    SENDGRID_API_URL,
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
                logger.error('SendGrid API HTTP error: %s — %s', exc, response.text)
                if not self.fail_silently:
                    raise
            except Exception as exc:
                logger.error('SendGrid API error: %s', exc)
                if not self.fail_silently:
                    raise

        return sent

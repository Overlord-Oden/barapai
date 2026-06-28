"""
Backend email custom utilisant l'API HTTP Brevo (ex-Sendinblue).
Utilise requests (déjà installé) au lieu de SMTP — contourne le blocage
des ports 587/465 sur Railway.
"""
import logging

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'


class BrevoEmailBackend(BaseEmailBackend):
    """Envoie les emails via l'API REST Brevo (port 443, jamais bloqué)."""

    def send_messages(self, email_messages):
        api_key = getattr(settings, 'BREVO_API_KEY', '')
        if not api_key:
            logger.error('BREVO_API_KEY non configuré — email non envoyé')
            return 0

        sent = 0
        for message in email_messages:
            from_email = message.from_email or settings.DEFAULT_FROM_EMAIL
            # Extrait nom et adresse depuis "Nom <email@domain.com>"
            if '<' in from_email:
                name, addr = from_email.split('<', 1)
                sender = {'name': name.strip(), 'email': addr.rstrip('>')}
            else:
                sender = {'name': 'Barapai', 'email': from_email}

            payload = {
                'sender': sender,
                'to': [{'email': addr} for addr in message.to],
                'subject': message.subject,
                'textContent': message.body,
            }

            try:
                response = requests.post(
                    BREVO_API_URL,
                    headers={
                        'api-key': api_key,
                        'Content-Type': 'application/json',
                    },
                    json=payload,
                    timeout=10,
                )
                response.raise_for_status()
                sent += 1
            except requests.HTTPError as exc:
                logger.error('Brevo API HTTP error: %s — %s', exc, response.text)
                if not self.fail_silently:
                    raise
            except Exception as exc:
                logger.error('Brevo API error: %s', exc)
                if not self.fail_silently:
                    raise

        return sent

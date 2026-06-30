from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Teste l envoi email et affiche la config active'

    def add_arguments(self, parser):
        parser.add_argument('--to', default='allassanedioms1@gmail.com')

    def handle(self, *args, **options):
        self.stdout.write('=== DIAGNOSTIC EMAIL ===')
        self.stdout.write(f"Backend   : {settings.EMAIL_BACKEND}")
        self.stdout.write(f"FROM      : {settings.DEFAULT_FROM_EMAIL}")
        api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        self.stdout.write(f"SENDGRID KEY : {'OK (' + api_key[:12] + '...)' if api_key else 'VIDE - NON CONFIGURE'}")
        sender_email = getattr(settings, 'SENDGRID_SENDER_EMAIL', '')
        self.stdout.write(f"SENDER    : {sender_email or 'VIDE'}")
        self.stdout.write('')

        recipient = options['to']
        self.stdout.write(f"Envoi vers {recipient}...")
        try:
            count = send_mail(
                subject='[Barapai] Test email',
                message='Ceci est un test. Si tu reçois cet email, la config Brevo fonctionne.',
                from_email=None,
                recipient_list=[recipient],
                fail_silently=False,
            )
            if count:
                self.stdout.write(self.style.SUCCESS(f'SUCCESS — {count} email envoyé'))
            else:
                self.stdout.write(self.style.WARNING('0 email envoyé (clé API vide ?)'))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f'ERREUR : {exc}'))

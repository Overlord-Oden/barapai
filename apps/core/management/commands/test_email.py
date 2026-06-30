import traceback

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Teste l envoi email et le flux mot de passe oublié'

    def add_arguments(self, parser):
        parser.add_argument('--to', default='allassanedioms1@gmail.com')
        parser.add_argument('--reset', action='store_true', help='Teste aussi le reset mot de passe')

    def handle(self, *args, **options):
        self.stdout.write('=== DIAGNOSTIC EMAIL ===')
        self.stdout.write(f"Backend   : {settings.EMAIL_BACKEND}")
        self.stdout.write(f"FROM      : {settings.DEFAULT_FROM_EMAIL}")
        api_key = getattr(settings, 'RESEND_API_KEY', '')
        self.stdout.write(f"RESEND KEY : {'OK (' + api_key[:8] + '...)' if api_key else 'VIDE - NON CONFIGURE'}")
        sender_email = getattr(settings, 'RESEND_FROM_EMAIL', '')
        self.stdout.write(f"SENDER    : {sender_email or 'VIDE'}")
        self.stdout.write('')

        recipient = options['to']

        if options['reset']:
            self._test_password_reset(recipient)
        else:
            self._test_simple(recipient)

    def _test_simple(self, recipient):
        self.stdout.write(f"Envoi simple vers {recipient}...")
        try:
            count = send_mail(
                subject='[Barapai] Test email',
                message='Ceci est un test. Si tu reçois cet email, la config Resend fonctionne.',
                from_email=None,
                recipient_list=[recipient],
                fail_silently=False,
            )
            if count:
                self.stdout.write(self.style.SUCCESS(f'SUCCESS — {count} email envoyé'))
            else:
                self.stdout.write(self.style.WARNING('0 email envoyé'))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f'ERREUR : {exc}'))

    def _test_password_reset(self, recipient):
        self.stdout.write(f"Test reset mot de passe vers {recipient}...")
        try:
            from django.contrib.auth.forms import PasswordResetForm
            from django.test import RequestFactory

            host = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'
            request = RequestFactory().get('/', HTTP_HOST=host)

            form = PasswordResetForm({'email': recipient})
            if not form.is_valid():
                self.stdout.write(self.style.ERROR(f'Formulaire invalide : {form.errors}'))
                return

            users = list(form.get_users(recipient))
            self.stdout.write(f"Utilisateurs trouvés : {len(users)}")
            for u in users:
                self.stdout.write(f"  → {u.email} active={u.is_active} usable_pwd={u.has_usable_password()}")

            if not users:
                self.stdout.write(self.style.WARNING('Aucun utilisateur actif avec cet email — aucun email envoyé'))
                return

            form.save(
                request=request,
                use_https=True,
                email_template_name='accounts/emails/password_reset_email.txt',
                subject_template_name='accounts/emails/password_reset_subject.txt',
            )
            self.stdout.write(self.style.SUCCESS('SUCCESS — email de reset envoyé'))
        except Exception:
            self.stdout.write(self.style.ERROR('ERREUR :'))
            self.stdout.write(traceback.format_exc())

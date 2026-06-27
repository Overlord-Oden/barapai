import logging

from django.core.mail import send_mail
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Review, ServiceRequest

logger = logging.getLogger(__name__)


def _update_average_rating(artisan_profile):
    avg = (
        Review.objects
        .filter(service_request__artisan=artisan_profile)
        .aggregate(avg=Avg('rating'))['avg']
    ) or 0
    artisan_profile.__class__.objects.filter(pk=artisan_profile.pk).update(
        average_rating=round(avg, 2)
    )


@receiver(post_save, sender=Review)
def on_review_saved(sender, instance, **kwargs):
    _update_average_rating(instance.service_request.artisan)


@receiver(post_delete, sender=Review)
def on_review_deleted(sender, instance, **kwargs):
    _update_average_rating(instance.service_request.artisan)


@receiver(post_save, sender=ServiceRequest)
def on_service_request_changed(sender, instance, created, **kwargs):
    """Email artisan (nouvelle demande) ou client (changement de statut)."""
    artisan_email = instance.artisan.user.email
    artisan_name = instance.artisan.user.full_name
    client_email = instance.client.email
    client_name = instance.client.full_name
    title = instance.title

    def _send(subject, message, recipient):
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[recipient],
                fail_silently=False,
            )
        except Exception as exc:
            logger.error("Barapai email failed — %s → %s : %s", subject, recipient, exc)

    if created:
        _send(
            subject=f"Nouvelle demande : {title}",
            message=(
                f"Bonjour {artisan_name},\n\n"
                f"{client_name} t'a envoyé une nouvelle demande :\n"
                f"« {title} »\n\n"
                f"Connecte-toi à ton dashboard pour accepter ou refuser.\n\n"
                f"— L'équipe Barapai"
            ),
            recipient=artisan_email,
        )
        return

    status_messages = {
        ServiceRequest.Status.ACCEPTED: (
            client_email,
            f"Ta demande a été acceptée — {title}",
            f"Bonjour {client_name},\n\n{artisan_name} a accepté ta demande « {title} ».\n"
            f"Tu peux lui écrire via la messagerie Barapai.\n\n— L'équipe Barapai",
        ),
        ServiceRequest.Status.REJECTED: (
            client_email,
            f"Ta demande n'a pas été retenue — {title}",
            f"Bonjour {client_name},\n\n{artisan_name} n'est pas disponible pour « {title} ».\n"
            f"D'autres artisans sont disponibles sur Barapai !\n\n— L'équipe Barapai",
        ),
        ServiceRequest.Status.COMPLETED: (
            client_email,
            "Mission terminée — laisse ton avis !",
            f"Bonjour {client_name},\n\nLa mission « {title} » avec {artisan_name} est terminée.\n"
            f"Prends 2 minutes pour laisser un avis !\n\n— L'équipe Barapai",
        ),
    }

    if instance.status in status_messages:
        recipient, subject, message = status_messages[instance.status]
        _send(subject=subject, message=message, recipient=recipient)

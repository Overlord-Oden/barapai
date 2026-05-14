"""
Modeles de l'app services : demandes, avis, messages.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class ServiceRequest(models.Model):
    """
    Demande de service d'un client vers un artisan.
    Entite transactionnelle centrale.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('En attente')
        ACCEPTED = 'ACCEPTED', _('Acceptee')
        REJECTED = 'REJECTED', _('Refusee')
        COMPLETED = 'COMPLETED', _('Terminee')
        CANCELLED = 'CANCELLED', _('Annulee')

    # Parties prenantes
    client = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='requests_made',
        limit_choices_to={'role': 'CLIENT'},
        verbose_name=_('Client'),
    )
    artisan = models.ForeignKey(
        'accounts.ArtisanProfile',
        on_delete=models.CASCADE,
        related_name='requests_received',
        verbose_name=_('Artisan'),
    )
    category = models.ForeignKey(
        'catalog.Category',
        on_delete=models.PROTECT,
        related_name='service_requests',
        verbose_name=_('Categorie'),
    )

    # Details de la demande
    title = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'))
    budget_min = models.PositiveIntegerField(_('Budget min (FCFA)'), null=True, blank=True)
    budget_max = models.PositiveIntegerField(_('Budget max (FCFA)'), null=True, blank=True)

    # Localisation de la prestation
    address = models.CharField(_('Adresse'), max_length=255, blank=True)
    latitude = models.FloatField(_('Latitude'), null=True, blank=True)
    longitude = models.FloatField(_('Longitude'), null=True, blank=True)

    # State machine
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(_('Termine le'), null=True, blank=True)

    class Meta:
        verbose_name = _('Demande de service')
        verbose_name_plural = _('Demandes de services')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'


class Review(models.Model):
    """
    Avis post-mission. Une seule review par ServiceRequest.
    """
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name=_('Mission'),
    )
    rating = models.PositiveSmallIntegerField(
        _('Note (1 a 5)'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(_('Commentaire'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Avis')
        verbose_name_plural = _('Avis')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.rating}/5 - {self.service_request.title}'


class Message(models.Model):
    """
    Message echange dans le contexte d'une ServiceRequest.
    Messagerie async simple (pas temps reel pour le MVP).
    """
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Demande'),
    )
    sender = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='messages_sent',
        verbose_name=_('Auteur'),
    )
    content = models.TextField(_('Contenu'))
    is_read = models.BooleanField(_('Lu'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['created_at']

    def __str__(self):
        return f'Message de {self.sender.full_name} - {self.created_at:%d/%m/%Y %H:%M}'
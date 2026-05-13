"""
Modeles de l'app accounts (utilisateurs et profils).
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager custom : l'email est l'identifiant unique au lieu du username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("L'email est obligatoire"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Le superuser doit avoir is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Le superuser doit avoir is_superuser=True'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    User custom de Barapai.
    On utilise l'email comme identifiant principal au lieu du username.
    """

    class Role(models.TextChoices):
        CLIENT = 'CLIENT', _('Client')
        ARTISAN = 'ARTISAN', _('Artisan')

    # On retire le champ username, on utilise l'email a la place
    username = None
    email = models.EmailField(_('Adresse email'), unique=True)

    # Champs custom Barapai
    phone = models.CharField(_('Telephone'), max_length=20, blank=True)
    full_name = models.CharField(_('Nom complet'), max_length=150)
    role = models.CharField(
        _('Role'),
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    is_phone_verified = models.BooleanField(_('Telephone verifie'), default=False)

    # Configuration d'authentification
    USERNAME_FIELD = 'email'  # email sert d'identifiant
    REQUIRED_FIELDS = ['full_name']  # demande lors de createsuperuser

    objects = UserManager()

    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')

    def __str__(self):
        return f'{self.full_name} ({self.email})'

    @property
    def is_artisan(self):
        return self.role == self.Role.ARTISAN

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT


from django.db import models

# Create your models here.

"""
Modeles de l'app catalog : categories de metiers et portfolio.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Categorie de metier (Plombier, Electricien, Menuisier...).
    Un artisan peut exercer plusieurs categories.
    """
    name = models.CharField(_('Nom'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True)
    icon = models.CharField(
        _('Icone (emoji ou nom)'),
        max_length=50,
        blank=True,
        help_text=_('Ex: 🔧 ou wrench (nom lucide-icon)'),
    )
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Categorie')
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def __str__(self):
        return self.name


class PortfolioImage(models.Model):
    """
    Photo de realisation dans le portfolio d'un artisan.
    """
    artisan = models.ForeignKey(
        'accounts.ArtisanProfile',
        on_delete=models.CASCADE,
        related_name='portfolio_images',
        verbose_name=_('Artisan'),
    )
    image = models.ImageField(_('Image'), upload_to='portfolio/')
    caption = models.CharField(_('Legende'), max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Photo de portfolio')
        verbose_name_plural = _('Photos de portfolio')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'Photo de {self.artisan.user.full_name}'
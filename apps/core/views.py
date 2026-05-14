"""
Vues de l'app core : pages publiques.
"""
from django.shortcuts import render

from catalog.models import Category


def home(request):
    """Page d'accueil publique."""
    categories = Category.objects.filter(is_active=True)
    return render(request, 'core/home.html', {
        'categories': categories,
    })
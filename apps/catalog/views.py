"""
Vues de l'app catalog : recherche d'artisans.
"""
from django.db.models import Q
from django.shortcuts import render

from accounts.models import ArtisanProfile

from .models import Category

from django.shortcuts import render, get_object_or_404

from services.models import Review


def artisans_list(request):
    """
    Liste des artisans avec recherche/filtres.
    Renvoie un partial si la requete vient de HTMX, page complete sinon.
    """
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    city = request.GET.get('city', '').strip()

    artisans = (
        ArtisanProfile.objects
        .select_related('user')
        .prefetch_related('categories')
    )

    if query:
        artisans = artisans.filter(
            Q(user__full_name__icontains=query) | Q(bio__icontains=query)
        )

    if category_slug:
        artisans = artisans.filter(categories__slug=category_slug)

    if city:
        artisans = artisans.filter(city__icontains=city)

    artisans = artisans.order_by('-is_available', '-average_rating', '-total_jobs')

    context = {
        'artisans': artisans,
        'categories': Category.objects.filter(is_active=True),
        'query': query,
        'selected_category': category_slug,
        'city': city,
    }

    # Si HTMX, on renvoie juste les resultats
    if request.htmx:
        return render(request, 'catalog/partials/_artisans_results.html', context)

    return render(request, 'catalog/artisans_list.html', context)





def artisan_detail(request, pk):
    """Page publique vitrine d'un artisan."""
    artisan = get_object_or_404(
        ArtisanProfile.objects
        .select_related('user')
        .prefetch_related('categories', 'portfolio_images'),
        pk=pk,
    )

    recent_reviews = (
        Review.objects
        .filter(service_request__artisan=artisan)
        .select_related('service_request__client')
        .order_by('-created_at')[:5]
    )

    return render(request, 'catalog/artisan_detail.html', {
        'artisan': artisan,
        'recent_reviews': recent_reviews,
    })
"""Vues de l'app services."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import ArtisanProfile

from .forms import ServiceRequestForm
from .models import ServiceRequest


@login_required
def create_service_request(request, artisan_pk):
    """Creer une demande de service pour un artisan donne."""
    if not request.user.is_client:
        messages.error(request, "Seuls les clients peuvent envoyer une demande.")
        return redirect('catalog:artisan_detail', pk=artisan_pk)

    artisan = get_object_or_404(ArtisanProfile, pk=artisan_pk)

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, artisan=artisan)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.client = request.user
            service_request.artisan = artisan
            service_request.save()
            messages.success(request, f"Demande envoyee a {artisan.user.full_name} !")
            return redirect('services:my_requests')
    else:
        form = ServiceRequestForm(artisan=artisan)

    return render(request, 'services/service_request_form.html', {
        'form': form,
        'artisan': artisan,
    })


@login_required
def my_requests(request):
    """Liste des demandes du client connecte."""
    requests_list = (
        request.user.requests_made
        .select_related('artisan__user', 'category')
        .order_by('-created_at')
    )
    return render(request, 'services/my_requests.html', {
        'requests_list': requests_list,
    })


@login_required
def artisan_dashboard(request):
    """Dashboard de l'artisan : ses missions recues."""
    if not request.user.is_artisan:
        messages.error(request, "Acces reserve aux artisans.")
        return redirect('core:home')

    artisan_profile = request.user.artisan_profile
    status_filter = request.GET.get('status', '')

    qs = artisan_profile.requests_received.select_related('client', 'category')
    if status_filter:
        qs = qs.filter(status=status_filter)
    qs = qs.order_by('-created_at')

    stats = {
        'all': artisan_profile.requests_received.count(),
        'pending': artisan_profile.requests_received.filter(status='PENDING').count(),
        'accepted': artisan_profile.requests_received.filter(status='ACCEPTED').count(),
        'completed': artisan_profile.requests_received.filter(status='COMPLETED').count(),
    }

    return render(request, 'services/artisan_dashboard.html', {
        'requests_list': qs,
        'status_filter': status_filter,
        'stats': stats,
    })


# Mapping action → (from_status, to_status) pour valider les transitions
ACTION_TRANSITIONS = {
    'accept': ('PENDING', 'ACCEPTED'),
    'reject': ('PENDING', 'REJECTED'),
    'complete': ('ACCEPTED', 'COMPLETED'),
}


@login_required
@require_POST
def update_request_status(request, pk, action):
    """Endpoint HTMX : changer le statut d'une demande."""
    service_request = get_object_or_404(ServiceRequest, pk=pk)

    # Verifier les droits
    if not request.user.is_artisan or request.user != service_request.artisan.user:
        return HttpResponseForbidden("Acces interdit.")

    # Verifier que l'action est valide
    if action not in ACTION_TRANSITIONS:
        return HttpResponseBadRequest("Action invalide.")

    from_status, to_status = ACTION_TRANSITIONS[action]
    if service_request.status != from_status:
        return HttpResponseBadRequest("Transition impossible depuis ce statut.")

    # Appliquer le changement
    service_request.status = to_status
    if to_status == 'COMPLETED':
        service_request.completed_at = timezone.now()
        service_request.artisan.total_jobs += 1
        service_request.artisan.save()
    service_request.save()

    return render(request, 'services/partials/_request_card_artisan.html', {
        'req': service_request,
    })
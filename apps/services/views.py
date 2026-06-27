"""Vues de l'app services."""
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import ArtisanProfile

from .forms import ServiceRequestForm, ReviewForm, MessageForm
from .models import ServiceRequest, Review, Message


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
    """Liste des demandes du client avec filtre par statut."""
    if request.user.is_artisan:
        return redirect('services:artisan_dashboard')

    status_filter = request.GET.get('status', '')
    valid_statuses = ('PENDING', 'ACCEPTED', 'COMPLETED', 'REJECTED', 'CANCELLED')

    qs = request.user.requests_made.select_related('artisan__user', 'category')
    if status_filter in valid_statuses:
        qs = qs.filter(status=status_filter)

    statuses = [
        ('PENDING', 'En attente'),
        ('ACCEPTED', 'Acceptées'),
        ('COMPLETED', 'Terminées'),
        ('REJECTED', 'Refusées'),
    ]
    return render(request, 'services/my_requests.html', {
        'requests_list': qs.order_by('-created_at'),
        'status_filter': status_filter,
        'statuses': statuses,
    })


@login_required
def artisan_dashboard(request):
    if not request.user.is_artisan:
        messages.error(request, "Accès réservé aux artisans.")
        return redirect('core:home')

    try:
        artisan_profile = request.user.artisan_profile
    except ArtisanProfile.DoesNotExist:
        messages.error(request, "Profil artisan introuvable.")
        return redirect('core:home')
    all_requests = artisan_profile.requests_received.all()

    stats = {
        'completed': all_requests.filter(status='COMPLETED').count(),
        'pending': all_requests.filter(status='PENDING').count(),
        'accepted': all_requests.filter(status='ACCEPTED').count(),
    }

    total_revenue = (
        all_requests.filter(status='COMPLETED').aggregate(total=Sum('budget_min'))
    )['total'] or 0

    status_filter = request.GET.get('status', 'PENDING')
    if status_filter not in ('PENDING', 'ACCEPTED', 'COMPLETED', 'REJECTED', 'CANCELLED'):
        status_filter = 'PENDING'

    pending_requests = (
        artisan_profile.requests_received
        .filter(status=status_filter)
        .select_related('client', 'category')
        .order_by('-created_at')
    )

    today = timezone.now().date()
    start_week = today - timedelta(days=today.weekday())
    days_labels = ['LUN', 'MAR', 'MER', 'JEU', 'VEN', 'SAM']
    week_data = []
    max_count = 1
    for i in range(6):
        day = start_week + timedelta(days=i)
        count = all_requests.filter(status='COMPLETED', completed_at__date=day).count()
        max_count = max(max_count, count)
        week_data.append({'label': days_labels[i], 'count': count, 'is_today': day == today})
    for d in week_data:
        d['height_pct'] = int((d['count'] / max_count) * 100) if max_count else 5

    return render(request, 'services/artisan_dashboard.html', {
        'artisan_profile': artisan_profile,
        'stats': stats,
        'total_revenue': total_revenue,
        'pending_requests': pending_requests,
        'status_filter': status_filter,
        'week_data': week_data,
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
        ArtisanProfile.objects.filter(pk=service_request.artisan_id).update(total_jobs=F('total_jobs') + 1)
    service_request.save()

    return render(request, 'services/partials/_request_card_artisan.html', {
        'req': service_request,
    })


@login_required
def conversation(request, pk):
    """Page de conversation (messages) liée à une demande de service."""
    service_request = get_object_or_404(
        ServiceRequest.objects.select_related('client', 'artisan__user', 'category'), pk=pk
    )

    is_client = request.user == service_request.client
    is_artisan = request.user == service_request.artisan.user

    if not (is_client or is_artisan):
        return HttpResponseForbidden("Accès interdit.")

    # Marquer les messages de l'autre partie comme lus
    service_request.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)

    form = MessageForm()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.service_request = service_request
            msg.sender = request.user
            msg.save()
            if request.htmx:
                messages_list = service_request.messages.select_related('sender').all()
                return render(request, 'services/partials/_messages_list.html', {
                    'messages_list': messages_list,
                    'current_user': request.user,
                })
            return redirect('services:conversation', pk=pk)

    messages_list = service_request.messages.select_related('sender').all()
    return render(request, 'services/conversation.html', {
        'service_request': service_request,
        'messages_list': messages_list,
        'form': form,
        'is_client': is_client,
    })


@login_required
def create_review(request, pk):
    """Laisser un avis sur une mission terminée (client uniquement)."""
    service_request = get_object_or_404(
        ServiceRequest.objects.select_related('artisan__user', 'client'), pk=pk
    )

    if request.user != service_request.client:
        return HttpResponseForbidden("Seul le client peut noter cette mission.")

    if service_request.status != ServiceRequest.Status.COMPLETED:
        messages.error(request, "Tu ne peux noter qu'une mission terminée.")
        return redirect('services:my_requests')

    if hasattr(service_request, 'review'):
        messages.info(request, "Tu as déjà noté cette mission.")
        return redirect('services:my_requests')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.service_request = service_request
            review.save()
            messages.success(request, f"Merci pour ton avis ! {review.rating}⭐")
            return redirect('services:my_requests')
    else:
        form = ReviewForm()

    return render(request, 'services/review_form.html', {
        'form': form,
        'service_request': service_request,
    })
"""
Vues de l'app accounts : signup, login, logout.
"""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import SignupForm, LoginForm, UserEditForm, ArtisanProfileForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue sur Barapai, {user.full_name} !")
            return redirect('core:home')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            messages.success(request, f"Bon retour, {form.user.full_name} !")
            next_url = request.GET.get('next') or 'core:home'
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Tu es deconnecte. A bientot !")
    return redirect('core:home')


@login_required
def profile_edit(request):
    """Édition du compte + du profil artisan si applicable."""
    user = request.user
    artisan_profile = getattr(user, 'artisan_profile', None)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        artisan_form = (
            ArtisanProfileForm(request.POST, request.FILES, instance=artisan_profile)
            if artisan_profile else None
        )
        user_valid = user_form.is_valid()
        artisan_valid = artisan_form.is_valid() if artisan_form else True

        if user_valid and artisan_valid:
            user_form.save()
            if artisan_form:
                artisan_form.save()
            messages.success(request, "Profil mis à jour avec succès !")
            return redirect('accounts:profile_edit')
    else:
        user_form = UserEditForm(instance=user)
        artisan_form = ArtisanProfileForm(instance=artisan_profile) if artisan_profile else None

    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'artisan_form': artisan_form,
    })
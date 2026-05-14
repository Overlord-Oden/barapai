"""
Vues de l'app accounts : signup, login, logout.
"""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import SignupForm, LoginForm


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
def logout_view(request):
    logout(request)
    messages.info(request, "Tu es deconnecte. A bientot !")
    return redirect('core:home')
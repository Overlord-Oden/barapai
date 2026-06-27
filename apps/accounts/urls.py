"""URLs de l'app accounts."""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profil/', views.profile_edit, name='profile_edit'),

    # Reset mot de passe (vues Django built-in, templates custom)
    path('mot-de-passe/reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/emails/password_reset_email.txt',
             subject_template_name='accounts/emails/password_reset_subject.txt',
             success_url='/accounts/mot-de-passe/reset/envoye/',
         ),
         name='password_reset'),
    path('mot-de-passe/reset/envoye/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html',
         ),
         name='password_reset_done'),
    path('mot-de-passe/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/mot-de-passe/reset/complet/',
         ),
         name='password_reset_confirm'),
    path('mot-de-passe/reset/complet/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html',
         ),
         name='password_reset_complete'),
]

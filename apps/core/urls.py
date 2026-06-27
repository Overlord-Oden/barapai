"""URLs de l'app core."""
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('cgu/', views.cgu, name='cgu'),
    path('confidentialite/', views.privacy, name='privacy'),
]

"""URLs de l'app catalog."""
from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.artisans_list, name='artisans_list'),
    path('<int:pk>/', views.artisan_detail, name='artisan_detail'),
]
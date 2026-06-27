"""URLs de l'app services."""
from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path('demander/<int:artisan_pk>/', views.create_service_request, name='create'),
    path('mes-demandes/', views.my_requests, name='my_requests'),
    path('artisan/', views.artisan_dashboard, name='artisan_dashboard'),
    path('<int:pk>/action/<str:action>/', views.update_request_status, name='update_status'),
    path('<int:pk>/messages/', views.conversation, name='conversation'),
    path('<int:pk>/avis/', views.create_review, name='create_review'),
]

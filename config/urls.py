"""
URL configuration for Barapai.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('artisans/', include('catalog.urls')),
    path('demandes/', include('services.urls')),
    path('', include('core.urls')),
]

# Pages d'erreur personnalisées (actives seulement en prod — DEBUG=False)
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

# En dev, on sert les fichiers media manuellement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
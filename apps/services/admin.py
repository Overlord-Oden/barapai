"""
Admin pour services : demandes, avis, messages.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import ServiceRequest, Review, Message


class MessageInline(admin.TabularInline):
    """Affiche les messages directement dans la page de la demande."""
    model = Message
    extra = 0
    readonly_fields = ('sender', 'content', 'is_read', 'created_at')
    can_delete = False


class ReviewInline(admin.StackedInline):
    """Affiche l'avis (s'il existe) directement dans la page de la demande."""
    model = Review
    extra = 0
    can_delete = False


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'artisan', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'client__email', 'artisan__user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline, ReviewInline]

    fieldsets = (
        (_('Parties prenantes'), {'fields': ('client', 'artisan', 'category')}),
        (_('Details'), {
            'fields': ('title', 'description', 'budget_min', 'budget_max'),
        }),
        (_('Localisation'), {
            'fields': ('address', 'latitude', 'longitude'),
        }),
        (_('Statut'), {
            'fields': ('status', 'completed_at'),
        }),
        (_('Dates'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('service_request', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'service_request__title')
    readonly_fields = ('created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'service_request', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__email')
    readonly_fields = ('created_at',) 
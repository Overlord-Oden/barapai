"""
Admin pour les modeles de l'app accounts.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, ArtisanProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'full_name', 'phone')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {
            'fields': ('full_name', 'phone', 'role', 'is_phone_verified'),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(ArtisanProfile)
class ArtisanProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'city', 'neighborhood', 'hourly_rate',
        'get_categories', 'is_available', 'is_verified_by_admin', 'average_rating',
    )
    list_filter = ('is_available', 'is_verified_by_admin', 'city')
    search_fields = ('user__email', 'user__full_name', 'bio')
    readonly_fields = ('average_rating', 'total_jobs', 'created_at', 'updated_at')
    filter_horizontal = ('categories',)

    fieldsets = (
        (_('Utilisateur'), {'fields': ('user',)}),
        (_('Profil professionnel'), {
            'fields': ('bio', 'years_experience', 'hourly_rate', 'is_available', 'categories', 'profile_picture'),
        }),
        (_('Localisation'), {
            'fields': ('city', 'neighborhood', 'latitude', 'longitude'),
        }),
        (_('Statistiques'), {
            'fields': ('average_rating', 'total_jobs'),
        }),
        (_('Verification'), {'fields': ('is_verified_by_admin',)}),
        (_('Dates'), {'fields': ('created_at', 'updated_at')}),
    )

    @admin.display(description=_('Categories'))
    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()]) or "—"
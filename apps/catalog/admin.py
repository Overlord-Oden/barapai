"""
Admin pour catalog : categories et portfolio.
"""
from django.contrib import admin

from .models import Category, PortfolioImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}  # auto-genere le slug depuis le nom


@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ('artisan', 'caption', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('artisan__user__full_name', 'caption')
    readonly_fields = ('uploaded_at',)
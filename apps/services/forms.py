"""Formulaires de l'app services."""
from django import forms

from .models import ServiceRequest, Review, Message


class ServiceRequestForm(forms.ModelForm):
    """
    Formulaire de creation d'une demande de service.
    L'artisan et le client sont definis par la vue, pas par l'utilisateur.
    """

    class Meta:
        model = ServiceRequest
        fields = ['category', 'title', 'description', 'budget_min', 'budget_max', 'address']
        widgets = {
            'category': forms.Select(),
            'title': forms.TextInput(attrs={'placeholder': 'Ex: Reparation porte armoire'}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Decris en detail le travail a effectuer...',
            }),
            'budget_min': forms.NumberInput(attrs={'placeholder': '5000'}),
            'budget_max': forms.NumberInput(attrs={'placeholder': '15000'}),
            'address': forms.TextInput(attrs={'placeholder': "Quartier ou lieu de l'intervention"}),
        }

    def __init__(self, *args, artisan=None, **kwargs):
        super().__init__(*args, **kwargs)
        if artisan:
            # Limiter le choix de categorie a celles de l'artisan
            self.fields['category'].queryset = artisan.categories.all()
            self.fields['category'].empty_label = '-- Choisis une categorie --'


class ReviewForm(forms.ModelForm):
    """Formulaire de notation post-mission (1 à 5 étoiles + commentaire)."""

    rating = forms.IntegerField(
        min_value=1, max_value=5,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': "Décris la qualité du travail, le sérieux de l'artisan...",
            }),
        }


class MessageForm(forms.ModelForm):
    """Formulaire d'envoi de message dans une conversation."""

    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Écris ton message...',
            }),
        }
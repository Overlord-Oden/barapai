"""Formulaires de l'app services."""
from django import forms

from .models import ServiceRequest


INPUT_CLASS = (
    'w-full px-4 py-2 border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-orange-500 focus:border-transparent'
)


class ServiceRequestForm(forms.ModelForm):
    """
    Formulaire de creation d'une demande de service.
    L'artisan et le client sont definis par la vue, pas par l'utilisateur.
    """

    class Meta:
        model = ServiceRequest
        fields = ['category', 'title', 'description', 'budget_min', 'budget_max', 'address']
        widgets = {
            'category': forms.Select(attrs={'class': INPUT_CLASS}),
            'title': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Ex: Reparation porte armoire',
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASS,
                'rows': 4,
                'placeholder': 'Decris en detail le travail a effectuer...',
            }),
            'budget_min': forms.NumberInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': '5000',
            }),
            'budget_max': forms.NumberInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': '15000',
            }),
            'address': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': "Quartier ou lieu de l'intervention",
            }),
        }

    def __init__(self, *args, artisan=None, **kwargs):
        super().__init__(*args, **kwargs)
        if artisan:
            # Limiter le choix de categorie a celles de l'artisan
            self.fields['category'].queryset = artisan.categories.all()
            self.fields['category'].empty_label = '-- Choisis une categorie --'
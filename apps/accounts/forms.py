"""
Formulaires pour l'authentification et l'édition de profil.
"""
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User, ArtisanProfile


class SignupForm(UserCreationForm):
    """Inscription. Si role=ARTISAN, on cree aussi un ArtisanProfile minimal."""

    full_name = forms.CharField(
        label=_('Nom complet'),
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Konan Yao'}),
    )
    phone = forms.CharField(
        label=_('Telephone'),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+225 07 00 00 00 00'}),
    )
    role = forms.ChoiceField(
        label=_('Je suis'),
        choices=User.Role.choices,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'role')
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'ton@email.com'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = _('Mot de passe')
        self.fields['password2'].label = _('Confirmer le mot de passe')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        user.phone = self.cleaned_data['phone']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
            # Si artisan, on cree son profil de base
            if user.role == User.Role.ARTISAN:
                ArtisanProfile.objects.create(user=user)
        return user


class LoginForm(forms.Form):
    """Connexion par email + mot de passe."""

    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': 'ton@email.com'}),
    )
    password = forms.CharField(
        label=_('Mot de passe'),
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # ModelBackend de Django attend 'username' qui correspond a USERNAME_FIELD (ici email)
            self.user = authenticate(username=email, password=password)
            if self.user is None:
                raise forms.ValidationError(_("Email ou mot de passe incorrect."))
            if not self.user.is_active:
                raise forms.ValidationError(_("Ce compte est desactive."))
        return cleaned_data


class UserEditForm(forms.ModelForm):
    """Édition des infos de base du compte (nom, téléphone, email)."""

    class Meta:
        model = User
        fields = ['full_name', 'phone', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Ton nom complet'}),
            'phone': forms.TextInput(attrs={'placeholder': '+225 07 00 00 00 00'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ton@email.com'}),
        }


class ArtisanProfileForm(forms.ModelForm):
    """Édition du profil professionnel artisan."""

    class Meta:
        model = ArtisanProfile
        fields = [
            'bio', 'years_experience', 'hourly_rate',
            'city', 'neighborhood', 'categories',
            'profile_picture', 'is_available',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Décris ton expertise, ton expérience, ce qui te différencie...',
            }),
            'years_experience': forms.NumberInput(attrs={'min': 0, 'max': 50}),
            'hourly_rate': forms.NumberInput(attrs={'placeholder': '5000'}),
            'city': forms.TextInput(attrs={'placeholder': 'Abidjan'}),
            'neighborhood': forms.TextInput(attrs={'placeholder': 'Cocody, Yopougon...'}),
            'categories': forms.CheckboxSelectMultiple(),
        }
from django.db.models import Count
from django.shortcuts import render
from catalog.models import Category
from accounts.models import ArtisanProfile


def home(request):
    categories = (
        Category.objects.filter(is_active=True)
        .annotate(artisan_count=Count('artisans', distinct=True))
        .order_by('name')
    )
    total_artisans = ArtisanProfile.objects.count()
    return render(request, 'core/home.html', {
        'categories': categories,
        'total_artisans': total_artisans,
    })


def contact(request):
    return render(request, 'core/contact.html')


def faq(request):
    faq_items = [
        ("Comment trouver un artisan sur Barapai ?", "Utilise la barre de recherche sur la page d'accueil. Filtre par métier, commune et budget. Consulte les profils et envoie une demande directement."),
        ("Les artisans sont-ils vraiment vérifiés ?", "Oui. Chaque artisan passe par une vérification manuelle de son identité et de ses compétences avant d'être visible sur la plateforme."),
        ("Comment fonctionne le paiement ?", "Le paiement se fait directement entre le client et l'artisan, en espèces ou via Mobile Money (Orange Money, Wave, MTN MoMo). Barapai n'intervient pas dans la transaction."),
        ("Comment laisser un avis ?", "Une fois une mission marquée comme terminée, tu peux noter l'artisan de 1 à 5 étoiles et laisser un commentaire depuis 'Mes demandes'."),
        ("Je suis artisan, comment m'inscrire ?", "Clique sur 'Devenir artisan' en haut de la page, crée ton compte, complète ton profil et tu seras visible immédiatement."),
        ("Comment modifier mon profil ?", "Connecte-toi et clique sur 'Mon profil' dans le menu. Tu peux mettre à jour tes informations, photos, catégories et tarif à tout moment."),
        ("Que faire si j'ai un problème avec un artisan ?", "Contacte-nous via le formulaire de contact. Notre équipe intervient dans les 24h pour trouver une solution."),
    ]
    return render(request, 'core/faq.html', {'faq_items': faq_items})


def cgu(request):
    return render(request, 'core/cgu.html')


def privacy(request):
    return render(request, 'core/privacy.html')


def handler404(request, exception=None):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)

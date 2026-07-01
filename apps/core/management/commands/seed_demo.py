"""
Commande pour peupler la base avec des données de démo réalistes.
Idempotente : ne crée pas de doublons si exécutée plusieurs fois.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import ArtisanProfile, User
from catalog.models import Category
from services.models import Review, ServiceRequest


CATEGORIES = [
    {'name': 'Plomberie', 'slug': 'plomberie', 'icon': '🔧'},
    {'name': 'Électricité', 'slug': 'electricite', 'icon': '⚡'},
    {'name': 'Menuiserie', 'slug': 'menuiserie', 'icon': '🪚'},
    {'name': 'Peinture', 'slug': 'peinture', 'icon': '🎨'},
    {'name': 'Climatisation', 'slug': 'climatisation', 'icon': '❄️'},
    {'name': 'Carrelage', 'slug': 'carrelage', 'icon': '🏗️'},
    {'name': 'Maçonnerie', 'slug': 'maconnerie', 'icon': '🧱'},
    {'name': 'Soudure', 'slug': 'soudure', 'icon': '🔥'},
    {'name': 'Informatique', 'slug': 'informatique', 'icon': '💻'},
    {'name': 'Électroménager', 'slug': 'electromenager', 'icon': '🛠️'},
]

ARTISANS = [
    {
        'email': 'kouassi.koffi@demo.barapai.ci',
        'full_name': 'Kouassi Koffi',
        'phone': '+225 07 01 23 45',
        'bio': 'Plombier professionnel avec 12 ans d\'expérience à Abidjan. Spécialisé dans l\'installation sanitaire, la réparation de fuites et la pose de chauffe-eau. Travail soigné, rapide et au juste prix.',
        'years_experience': 12,
        'hourly_rate': 8000,
        'neighborhood': 'Cocody',
        'categories': ['Plomberie'],
        'average_rating': 4.8,
        'total_jobs': 127,
        'is_verified': True,
    },
    {
        'email': 'amara.diallo@demo.barapai.ci',
        'full_name': 'Amara Diallo',
        'phone': '+225 05 44 67 89',
        'bio': 'Électricien certifié, formé à l\'INPHB. Installation électrique, dépannage, tableau électrique, prises et interrupteurs. Intervention rapide 7j/7 sur tout Abidjan.',
        'years_experience': 8,
        'hourly_rate': 10000,
        'neighborhood': 'Marcory',
        'categories': ['Électricité'],
        'average_rating': 4.9,
        'total_jobs': 89,
        'is_verified': True,
    },
    {
        'email': 'yao.mensah@demo.barapai.ci',
        'full_name': 'Yao Mensah',
        'phone': '+225 01 56 78 90',
        'bio': 'Menuisier ébéniste depuis 15 ans. Fabrication sur mesure de meubles, portes, fenêtres et placards. Matériaux de qualité, finition impeccable. Devis gratuit à domicile.',
        'years_experience': 15,
        'hourly_rate': 12000,
        'neighborhood': 'Yopougon',
        'categories': ['Menuiserie'],
        'average_rating': 4.7,
        'total_jobs': 203,
        'is_verified': True,
    },
    {
        'email': 'adjoua.bamba@demo.barapai.ci',
        'full_name': 'Adjoua Bamba',
        'phone': '+225 07 89 12 34',
        'bio': 'Peintre en bâtiment spécialisée dans la décoration intérieure. Ravalement de façades, peinture murale, enduits décoratifs et textures. Couleurs tendance, résultat professionnel garanti.',
        'years_experience': 6,
        'hourly_rate': 6000,
        'neighborhood': 'Plateau',
        'categories': ['Peinture'],
        'average_rating': 4.6,
        'total_jobs': 74,
        'is_verified': True,
    },
    {
        'email': 'seydou.toure@demo.barapai.ci',
        'full_name': 'Seydou Touré',
        'phone': '+225 05 23 45 67',
        'bio': 'Technicien froid & climatisation agréé. Installation, maintenance et dépannage de tous types de climatiseurs (split, cassette, gainable). Réponse en moins de 2h sur Abidjan.',
        'years_experience': 10,
        'hourly_rate': 15000,
        'neighborhood': 'Treichville',
        'categories': ['Climatisation', 'Électroménager'],
        'average_rating': 4.9,
        'total_jobs': 156,
        'is_verified': True,
    },
    {
        'email': 'konan.assi@demo.barapai.ci',
        'full_name': 'Konan Assi',
        'phone': '+225 01 34 56 78',
        'bio': 'Carreleur professionnel, 9 ans de métier. Pose de carrelage sol et mur, faïence, mosaïque. Découpe laser pour joints parfaits. Salles de bain, cuisines, terrasses et piscines.',
        'years_experience': 9,
        'hourly_rate': 9000,
        'neighborhood': 'Adjamé',
        'categories': ['Carrelage'],
        'average_rating': 4.5,
        'total_jobs': 98,
        'is_verified': True,
    },
    {
        'email': 'ibrahim.coulibaly@demo.barapai.ci',
        'full_name': 'Ibrahim Coulibaly',
        'phone': '+225 07 67 89 01',
        'bio': 'Maçon et chef de chantier avec 18 ans d\'expérience. Construction, rénovation, extension de maison, chape, enduits. Coordination d\'équipe pour grands projets. Devis détaillé et transparent.',
        'years_experience': 18,
        'hourly_rate': 7500,
        'neighborhood': 'Abobo',
        'categories': ['Maçonnerie'],
        'average_rating': 4.7,
        'total_jobs': 312,
        'is_verified': True,
    },
    {
        'email': 'mawa.sangare@demo.barapai.ci',
        'full_name': 'Mawa Sangaré',
        'phone': '+225 05 78 90 12',
        'bio': 'Technicienne informatique, réparation PC et Mac, récupération de données, installation de logiciels, réseau WiFi et câblé. Intervention à domicile ou en entreprise. Tarif honnête.',
        'years_experience': 5,
        'hourly_rate': 7000,
        'neighborhood': 'Cocody',
        'categories': ['Informatique'],
        'average_rating': 4.8,
        'total_jobs': 61,
        'is_verified': True,
    },
    {
        'email': 'daouda.ouattara@demo.barapai.ci',
        'full_name': 'Daouda Ouattara',
        'phone': '+225 01 90 12 34',
        'bio': 'Soudeur qualifié, ferronnerie d\'art et soudure industrielle. Fabrication de portails, grilles de sécurité, escaliers métalliques, garde-corps. Galvanisation anti-rouille disponible.',
        'years_experience': 11,
        'hourly_rate': 11000,
        'neighborhood': 'Koumassi',
        'categories': ['Soudure'],
        'average_rating': 4.6,
        'total_jobs': 88,
        'is_verified': True,
    },
    {
        'email': 'aya.kone@demo.barapai.ci',
        'full_name': 'Aya Koné',
        'phone': '+225 07 12 34 56',
        'bio': 'Plombière et sanitariste. Installation de douches, baignoires, WC, lavabos et ballons d\'eau chaude. Détection de fuites, débouchage de canalisations. 10 ans de terrain à Abidjan.',
        'years_experience': 10,
        'hourly_rate': 8500,
        'neighborhood': 'Marcory',
        'categories': ['Plomberie', 'Électroménager'],
        'average_rating': 4.9,
        'total_jobs': 143,
        'is_verified': True,
    },
    {
        'email': 'felix.gnagne@demo.barapai.ci',
        'full_name': 'Félix Gnagné',
        'phone': '+225 05 45 67 89',
        'bio': 'Électricien industriel et domestique. Tableau électrique, câblage complet, éclairage LED, domotique et énergie solaire. Certifié Consuel. Disponible week-ends et jours fériés.',
        'years_experience': 13,
        'hourly_rate': 12000,
        'neighborhood': 'Yopougon',
        'categories': ['Électricité'],
        'average_rating': 4.7,
        'total_jobs': 175,
        'is_verified': True,
    },
    {
        'email': 'mariam.traore@demo.barapai.ci',
        'full_name': 'Mariam Traoré',
        'phone': '+225 01 23 45 67',
        'bio': 'Peintre décoratrice, spécialiste stuc vénitien et trompe-l\'œil. Relooking d\'appartements, peinture de meubles, décoration murale sur mesure. Diplômée des arts appliqués de Paris.',
        'years_experience': 7,
        'hourly_rate': 9000,
        'neighborhood': 'Cocody',
        'categories': ['Peinture'],
        'average_rating': 5.0,
        'total_jobs': 52,
        'is_verified': True,
    },
]

CLIENTS = [
    {
        'email': 'demo.client@barapai.ci',
        'full_name': 'Marie Kouamé',
        'phone': '+225 07 00 11 22',
        'password': 'DemoClient2026',
    },
    {
        'email': 'jean.paul@demo.barapai.ci',
        'full_name': 'Jean-Paul Akré',
        'phone': '+225 05 33 44 55',
        'password': 'DemoClient2026',
    },
]


class Command(BaseCommand):
    help = 'Peuple la base avec des données de démo réalistes (Abidjan)'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('=== SEED DEMO BARAPAI ===\n')

        # 1. Catégories
        self.stdout.write('Création des catégories...')
        cat_map = {}
        for c in CATEGORIES:
            obj, created = Category.objects.get_or_create(
                slug=c['slug'],
                defaults={'name': c['name'], 'icon': c['icon'], 'is_active': True},
            )
            cat_map[c['name']] = obj
            if created:
                self.stdout.write(f"  + {obj.name}")
        self.stdout.write(self.style.SUCCESS(f'  {len(cat_map)} catégories OK\n'))

        # 2. Artisans
        self.stdout.write('Création des artisans...')
        artisan_profiles = []
        for a in ARTISANS:
            user, created = User.objects.get_or_create(
                email=a['email'],
                defaults={
                    'full_name': a['full_name'],
                    'phone': a['phone'],
                    'role': User.Role.ARTISAN,
                    'is_active': True,
                },
            )
            if created:
                user.set_password('ArtisanDemo2026')
                user.save()

            profile, _ = ArtisanProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': a['bio'],
                    'years_experience': a['years_experience'],
                    'hourly_rate': a['hourly_rate'],
                    'neighborhood': a['neighborhood'],
                    'city': 'Abidjan',
                    'average_rating': a['average_rating'],
                    'total_jobs': a['total_jobs'],
                    'is_verified_by_admin': a['is_verified'],
                    'is_available': True,
                },
            )
            # Assigner les catégories
            for cat_name in a['categories']:
                if cat_name in cat_map:
                    profile.categories.add(cat_map[cat_name])

            artisan_profiles.append(profile)
            self.stdout.write(f"  + {a['full_name']} ({a['neighborhood']})")

        self.stdout.write(self.style.SUCCESS(f'  {len(ARTISANS)} artisans OK\n'))

        # 3. Clients
        self.stdout.write('Création des clients de démo...')
        client_users = []
        for c in CLIENTS:
            user, created = User.objects.get_or_create(
                email=c['email'],
                defaults={
                    'full_name': c['full_name'],
                    'phone': c['phone'],
                    'role': User.Role.CLIENT,
                    'is_active': True,
                },
            )
            if created:
                user.set_password(c['password'])
                user.save()
            client_users.append(user)
            self.stdout.write(f"  + {c['full_name']}")
        self.stdout.write(self.style.SUCCESS(f'  {len(CLIENTS)} clients OK\n'))

        # 4. Demandes + avis de démo
        self.stdout.write('Création des demandes et avis...')
        demo_requests = [
            {
                'client': client_users[0],
                'artisan': artisan_profiles[0],
                'category': cat_map['Plomberie'],
                'title': 'Réparation fuite sous évier cuisine',
                'description': 'Fuite importante sous l\'évier de la cuisine. Besoin d\'une intervention rapide.',
                'budget_min': 15000, 'budget_max': 30000,
                'address': 'Cocody Riviera 3, Abidjan',
                'status': ServiceRequest.Status.COMPLETED,
                'review': {'rating': 5, 'comment': 'Excellent travail, très professionnel et ponctuel. Je recommande vivement !'},
            },
            {
                'client': client_users[0],
                'artisan': artisan_profiles[1],
                'category': cat_map['Électricité'],
                'title': 'Installation de 5 prises électriques',
                'description': 'Besoin d\'installer 5 nouvelles prises dans le salon et les chambres.',
                'budget_min': 25000, 'budget_max': 50000,
                'address': 'Marcory Zone 4, Abidjan',
                'status': ServiceRequest.Status.COMPLETED,
                'review': {'rating': 5, 'comment': 'Travail impeccable, câblage propre et bien rangé. Très satisfait.'},
            },
            {
                'client': client_users[1],
                'artisan': artisan_profiles[4],
                'category': cat_map['Climatisation'],
                'title': 'Maintenance climatiseur salon',
                'description': 'Nettoyage et vérification du climatiseur split du salon.',
                'budget_min': 10000, 'budget_max': 20000,
                'address': 'Treichville, Abidjan',
                'status': ServiceRequest.Status.ACCEPTED,
                'review': None,
            },
            {
                'client': client_users[1],
                'artisan': artisan_profiles[2],
                'category': cat_map['Menuiserie'],
                'title': 'Fabrication armoire chambre principale',
                'description': 'Armoire encastrée sur mesure, 2m50 de largeur, avec miroir.',
                'budget_min': 150000, 'budget_max': 250000,
                'address': 'Yopougon Selmer, Abidjan',
                'status': ServiceRequest.Status.PENDING,
                'review': None,
            },
        ]

        created_count = 0
        for req_data in demo_requests:
            exists = ServiceRequest.objects.filter(
                client=req_data['client'],
                artisan=req_data['artisan'],
                title=req_data['title'],
            ).exists()
            if not exists:
                req = ServiceRequest.objects.create(
                    client=req_data['client'],
                    artisan=req_data['artisan'],
                    category=req_data['category'],
                    title=req_data['title'],
                    description=req_data['description'],
                    budget_min=req_data['budget_min'],
                    budget_max=req_data['budget_max'],
                    address=req_data['address'],
                    status=req_data['status'],
                )
                if req_data['review']:
                    Review.objects.create(
                        service_request=req,
                        rating=req_data['review']['rating'],
                        comment=req_data['review']['comment'],
                    )
                created_count += 1
                self.stdout.write(f"  + {req_data['title'][:50]}")

        self.stdout.write(self.style.SUCCESS(f'  {created_count} demandes OK\n'))

        # Résumé
        self.stdout.write('=' * 40)
        self.stdout.write(self.style.SUCCESS('SEED TERMINÉ'))
        self.stdout.write(f"  Catégories : {Category.objects.count()}")
        self.stdout.write(f"  Artisans   : {ArtisanProfile.objects.count()}")
        self.stdout.write(f"  Clients    : {User.objects.filter(role=User.Role.CLIENT).count()}")
        self.stdout.write(f"  Demandes   : {ServiceRequest.objects.count()}")
        self.stdout.write(f"  Avis       : {Review.objects.count()}")
        self.stdout.write('')
        self.stdout.write('Comptes de démo :')
        self.stdout.write('  CLIENT  : demo.client@barapai.ci / DemoClient2026')
        self.stdout.write('  ARTISAN : kouassi.koffi@demo.barapai.ci / ArtisanDemo2026')

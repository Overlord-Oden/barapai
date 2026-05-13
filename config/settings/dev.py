"""
Settings pour le developpement local.
"""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Affiche les emails dans la console au lieu de les envoyer
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = ['127.0.0.1']
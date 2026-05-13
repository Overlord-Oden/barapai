#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    # Ajoute le dossier apps/ au PYTHONPATH (pour Phase 2B)
    BASE_DIR = Path(__file__).resolve().parent
    sys.path.insert(0, str(BASE_DIR / 'apps'))

    # Par defaut on utilise les settings de dev
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Vérifie que ton venv est activé."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
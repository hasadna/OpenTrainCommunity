"""
WSGI config for train2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
env_or_default_settings = os.getenv('DJANGO_SETTINGS_MODULE', 'train2.settings.dev_settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', env_or_default_settings)

application = get_wsgi_application()

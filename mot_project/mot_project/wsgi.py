"""
WSGI config for interface_experimentation project.

It exposes the WSGI callable as a get_bandits-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mot_project.settings')

application = get_wsgi_application()

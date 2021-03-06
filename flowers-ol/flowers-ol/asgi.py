"""
ASGI config for interface_experimentation project.

It exposes the ASGI callable as a get_bandits-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'experiment_manager_app.settings')

application = get_asgi_application()

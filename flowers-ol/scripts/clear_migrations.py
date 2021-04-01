#!/usr/bin/python

import os, sys, django
from django.conf import settings


# Get list of user-defined apps
sys.path.append(
    # Append absolute path to project directory (one level up from __file__) to PYTHONPATH
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowers-ol.settings')
django.setup()
apps = settings.USER_APPS


if __name__ == '__main__':
    for app in apps:
        if os.path.isdir(f'{app}/migrations'):
            os.system(f'rm -rf {app}/migrations')
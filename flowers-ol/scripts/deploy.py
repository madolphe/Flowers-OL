#!/usr/bin/python

import sys
import getopt, argparse
import os
import django
from django.conf import settings


# Get list of user-defined apps
sys.path.append(
    # Append absolute path to project directory (one level up from __file__) to PYTHONPATH
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowers-ol.settings')
django.setup()
apps = settings.USER_APPS

# Parse arguments
p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('-r', '--reset_db', action='store_true', help='Boolean flag to reset project database using reset_db')
p.add_argument('-s', '--superuser', action='store_true', help='Boolean flag to create superuser')
p.add_argument('-c', '--collectstatic', action='store_true', help='Boolean flag to collect static files inside STATIC_ROOT')
p.add_argument('-t', '--translate', action='store_true', help='Boolean flag to register translation fields')
p.add_argument('-f', '--full', action='store_true', help='Boolean flag to run deployment will all options')
args = p.parse_args()


if __name__ == '__main__':
    pipenv_pref = 'pipenv run python manage.py' if os.getenv('PIPENV_ACTIVE') != '1' else 'pipenv run python manage.py'

    # If user wants to reset db:
    if args.reset_db or args.full:
        os.system(f'{pipenv_pref} reset_db')
        print()

    # Make sure a migration folder exists:
    for app in apps:
        if not os.path.isdir(f'{app}/migrations'):
            os.system(f'mkdir {app}/migrations')
            os.system(f'touch {app}/migrations/__init__.py')

    # List of `manage.py` commands to run (order is important!)
    # 1. Make migrations
    # 2. Apply migrations
    labels = ['Making migrations', 'Migrating']
    commands = ['makemigrations', 'migrate']

    # 3. Register translation fields
    commands.append('sync_translation_fields')
    labels.append('Registering translation fields')

    # Install fixtures for each app
    for app in apps:
        if os.path.isdir(f'{app}/fixtures'):
            commands.append(f'loaddata {app}/fixtures/*')
            labels.append(f'Loading fixtures for {app}')

    # 4. Collect statics (optional)
    if args.collectstatic or args.full:
        commands.append('collectstatic -l')
        labels.append('Collecting static files')

    # 5. Add superuser (optional)
    if args.superuser or args.full:
        commands.append('createsuperuser')
        labels.append('Creating superuser')

    # Run commands synchronoulsy
    for label, command in zip(labels, commands):
        print()
        print(f'* {label} ...')
        if os.system(f'{pipenv_pref} {command}') == 0:
            continue

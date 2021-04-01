#!/usr/bin/env python

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
p.add_argument('-a', '--all', action='store_true', help='Boolean flag to run deployment will all options')
p.add_argument('-r', '--reset_db', action='store_true', help='Boolean flag to reset project database using reset_db')
p.add_argument('-s', '--superuser', action='store_true', help='Boolean flag to create superuser')
p.add_argument('-c', '--collectstatic', action='store_true', help='Boolean flag to collect static files inside STATIC_ROOT')
p.add_argument('-t', '--translations', action='store_true', help='Boolean flag to run translation routines across all apps (i.e. makemessages and sync_translation_fields)')
p.add_argument('-m', '--migrations', action='store_true', help='Boolean flag to make and apply migrations across all apps')
p.add_argument('-f', '--fixtures', action='store_true', help='Boolean flag to install fixtures across all apps')
args = p.parse_args()


# Add text ANSI escape sequences for pretty text output
class bcolors:
    PURPLE_BOLD_BRIGHT = '\033[1;95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def bold(s):
    return f'{bcolors.BOLD}{s}{bcolors.ENDC}'


class Deployer(object):
    def __init__(self):
        self.commands = []
        self.messages = []

    def highlight_message(self, message):
        # return f'{bcolors.HEADER}{bcolors.PURPLE}* {message} ...{bcolors.ENDC}{bcolors.ENDC}'
        return f'{bcolors.PURPLE_BOLD_BRIGHT}* {message} ...{bcolors.ENDC}'

    def add(self, command='', message='', plain_format=False):
        assert any([command, message]), 'Need either a command or a message to add'
        self.commands.append(command)
        self.messages.append(message if plain_format else self.highlight_message(message))

    def run(self):
        for message, command in zip(self.messages, self.commands):
            if message:
                print(message)
            if os.system(f'{command}') == 0:
                continue
            else:
                break


def main():
    deployer = Deployer()
    prefix = 'python manage.py' if os.getenv('PIPENV_ACTIVE') != '1' else 'pipenv run python manage.py'
    # deployer.add(f'{}', '')
    # If user wants to reset db:
    if args.reset_db or args.all:
        deployer.add(command=f'{prefix} reset_db', message='Resetting DB')
    
    # Mogrations
    if args.migrations or args.all:
        deployer.add(message='Setting up migration directories')
        for app in apps:
            # Make sure a migration folder exists, if not create one and add __init__.py inside
            if not os.path.isdir(f'{app}/migrations'):
                deployer.add(f'mkdir {app}/migrations', f'  mkdir {bold(app)}/migrations', plain_format=True)
                deployer.add(f'touch {app}/migrations/__init__.py', f'  touch {bold(app)}/migrations/__init__.py', plain_format=True)
            else:
                deployer.add('', f'  migration directory is already set up for {bold(app)}', plain_format=True)
        deployer.add(f'{prefix} makemigrations', 'Creating migrations')
        deployer.add(f'{prefix} migrate', 'Migrating')

    # Register translation fields
    # TODO add code to make messages in all apps
    if args.translations or args.all:
        deployer.add(f'{prefix} sync_translation_fields', 'Registering translation fields')

    # Install fixtures for each app
    if args.fixtures or args.all:
        deployer.add(message='Installing fixtures')
        for app in apps:
            if os.path.isdir(f'{app}/fixtures'):
                deployer.add(f'{prefix} loaddata {app}/fixtures/* -v 1', f'  {bold(app)}', plain_format=True)

    # Collect statics
    if args.collectstatic or args.all:
        deployer.add(f'{prefix} collectstatic -l', 'Collecting static files')

    # Add superuser
    if args.superuser or args.all:
        deployer.add(f'{prefix} createsuperuser', 'Creating superuser')

    deployer.run()


if __name__ == '__main__':
    main()

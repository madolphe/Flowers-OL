#!/usr/bin/env python

import sys
import getopt, argparse
import os
import django
from django.conf import settings
from django.core.management import call_command

# Get list of user-defined apps
sys.path.append(
    # Append absolute path to project directory (one level up from __file__) to PYTHONPATH
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowers-ol.flowers-ol.settings')

django.setup()
apps = settings.USER_APPS

# Parse arguments
p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('-a', '--all', action='store_true', help='Boolean flag to run deployment will all options')
p.add_argument('-r', '--reset_db', action='store_true', help='Boolean flag to reset project database using reset_db')
p.add_argument('-s', '--superuser', action='store_true', help='Boolean flag to create superuser')
p.add_argument('-c', '--collectstatic', action='store_true',
               help='Boolean flag to collect static files inside STATIC_ROOT')
p.add_argument('-t', '--translations', action='store_true',
               help='Boolean flag to run translation routines across all apps (i.e. makemessages and sync_translation_fields)')
p.add_argument('-m', '--migrations', action='store_true',
               help='Boolean flag to make and apply migrations across all apps')
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
        self.os_commands = []
        self.dj_commands = []
        self.messages = []
        self.rm_list = []

    def highlight_message(self, message):
        # return f'{bcolors.HEADER}{bcolors.PURPLE}* {message} ...{bcolors.ENDC}{bcolors.ENDC}'
        return f'{bcolors.PURPLE_BOLD_BRIGHT}* {message} ...{bcolors.ENDC}'

    def add(self, os_command='', django_command=None, message='', plain_format=False):
        assert any([os_command, django_command, message]), 'Need either a command or a message to add'
        self.os_commands.append(os_command)
        self.dj_commands.append(django_command)
        self.messages.append(message if plain_format else self.highlight_message(message))

    def run(self):
        print(self.os_commands)
        for message, os_command, dj_command in zip(self.messages, self.os_commands, self.dj_commands):
            if message:
                print(message)
            if dj_command:
                try:
                    if type(dj_command) == dict:
                        call_command(**dj_command)
                    else:
                        call_command(dj_command)
                except Exception as e:
                    print(e)
            if os.system(f'{os_command}') == 0:
                continue
            else:
                break


locales = ['en']


def main():
    deployer = Deployer()
    if args.reset_db or args.all:
        # If user wants to reset db:
        # First reset database
        deployer.add(django_command={"command_name": 'reset_db', "noinput": False}, message='Resetting DB')
        # Then clear migration directories
        deployer.add(message='Removing migration directories')
        for app in apps:
            if os.path.isdir(f'{app}/migrations'):
                deployer.add(os_command=f'rm -rf {app}/migrations', message=f'  rm -r -f {bold(app)}/migrations',
                             plain_format=True)
                deployer.rm_list.append(f'{app}/migrations')
            else:
                deployer.add(message=f'  No migration directory in {bold(app)}', plain_format=True)

    # Migrations
    if args.migrations or args.all:
        deployer.add(message='Setting up migration directories')
        for app in apps:
            # Make sure a migration folder exists, if not create one and add __init__.py inside
            if not os.path.isdir(f'flowers-ol/{app}/migrations') or (
                    f'flowers-ol/{app}/migrations' in deployer.rm_list):
                deployer.add(
                    os_command=f'mkdir flowers-ol/{app}/migrations ; touch flowers-ol/{app}/migrations/__init__.py',
                    message=f'  mkdir {bold(app)}/migrations ; touch {bold(app)}/migrations/__init__.py',
                    plain_format=True)
            else:
                deployer.add(os_command='', message=f'  directory {bold(app)} already exists', plain_format=True)
                deployer.add(os_command=f'ls flowers-ol/{app}/migrations', message='')
        deployer.add(django_command={'command_name': 'makemigrations'}, message='Creating migrations')
        deployer.add(django_command={'command_name': 'migrate'}, message='Migrating')

    # Internationalization routines
    if args.translations or args.all:
        deployer.add(message='Checking locale directories')
        for app in apps:
            if os.path.isdir(f'flowers-ol/{app}/locale'):
                deployer.add(message=f'  locale directory found for {bold(app)} -- generating .po files',
                             plain_format=True)
            else:
                deployer.add(message=f'  locale directory NOT found in {bold(app)} -- moving on', plain_format=True)
        deployer.add(
            django_command={"command_name": "makemessages", "locale": ["en"], "ignore": ['*/.venv/*', '*/.git/*'],
                            "no_default_ignore": True, "verbosity": 3},
            message=f'Making messages for locales in {locales}')
        deployer.add(django_command={'command_name': 'compilemessages', "ignore": ['*/.venv/*', '*/.git/*'],
                                     "verbosity": 3}, message='Compiling messages')
    # Register translation fields
    # if args.translations or args.all:
    #     deployer.add(f'{prefix} sync_translation_fields', 'Registering translation fields')

    # Install fixtures for each app
    if args.fixtures or args.all:
        deployer.add(message='Installing fixtures')
        for app in apps:
            if os.path.isdir(f'flowers-ol/{app}/fixtures'):
                deployer.add(
                    django_command={"command_name": "loaddata", "args": "flowers-ol/{app}/fixtures/*", "verbose": 1},
                    message=f'  {bold(app)}',
                    plain_format=True)

    # Collect statics
    if args.collectstatic or args.all:
        deployer.add(django_command={"command_name": "collectstatic", "no_input": False, "clear": True, "link": False},
                     message='Collecting static files')

    # Add superuser
    if args.superuser or args.all:
        deployer.add(
            django_command={"command_name": "createsuperuser",
                            "no_input": False},
            # "password": os.getenv("DJANGO_SUPERUSER_PASSWORD"),
            # "email": os.getenv("DJANGO_SUPERUSER_EMAIL"),
            # "username": os.getenv("DJANGO_SUPERUSER_USERNAME")},
            message='Creating superuser')
    deployer.run()


if __name__ == '__main__':
    main()

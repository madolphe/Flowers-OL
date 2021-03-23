#!/usr/bin/python

import sys
import getopt
import os

application_names = ['experiment_manager_app', 'mot_app', 'survey_app', 'jold_app']


def get_args(argv):
    try:
        opts, args = getopt.getopt(argv, "hr")
    except getopt.GetoptError:
        print('Usage: python deploy.py -r <boolean>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python deploy.py -r <boolean>')
            sys.exit()
        elif opt in ("-r", "--reset_db"):
            return True
        return False


if __name__ == "__main__":
    pipenv_pref = "pipenv run python manage.py" if os.getenv('PIPENV_ACTIVE') != '1' else "python manage.py"

    # If user wants to reset db:
    if get_args(sys.argv[1:]):
        os.system(f'{pipenv_pref} reset_db')

    # Make sure a migration folder exists:
    for app in application_names:
        if not os.path.isdir(f'{app}/migrations'):
            os.system(f'mkdir {app}/migrations')
            os.system(f'touch {app}/migrations/__init__.py')

    # List of commands to run:
    commands = ['makemigrations', 'migrate', 'sync_translation_fields']
    # Then loaddata:
    for app in application_names:
        if os.path.isdir(f'{app}/fixtures'):
            commands.append(f'loaddata {app}/fixtures/*')
    # Finally collectstatics and add superuser
    commands += ['collectstatic -l', 'createsuperuser']

    # To make sure cmds are run synchronoulsy:
    for command in commands:
        if 'loaddata' in command:
            app = command.split(' ')[1].split('/')[0].upper()
            print(f'Loading fixtures for {app}')
        if os.system(f'{pipenv_pref} {command}') == 0:
            continue

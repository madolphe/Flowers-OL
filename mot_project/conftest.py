import pytest
from django.core.management import call_command


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'interface_app/fixtures/Studies.json')
        call_command('loaddata', 'interface_app/fixtures/JOLDQuestions.json')
        call_command('loaddata', 'interface_app/fixtures/MOTQuestions.json')
        call_command('loaddata', 'interface_app/fixtures/JOLDTasks.json')
        call_command('loaddata', 'interface_app/fixtures/MOTTasks.json')
        call_command('loaddata', 'interface_app/fixtures/JOLDSessions.json')
        call_command('loaddata', 'interface_app/fixtures/MOTSessions.json')

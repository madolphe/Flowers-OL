import uuid

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Study

# FIRST TESTS ON DB : LOOK FOR STUDY, TASKS AND QUESTIONS #
# THEN CREATE USER AND PARTICIPANT THKS TO SIGN IN VIEW #
# THEN TRY TO CONNECT THANKS TO LOGIN PAGE #
# TRY TO CONNECT WITH NO ACCOUNT #
# ASSERT THAT IT IS NOT POSSIBLE TO SIGN IN WHEN NOT THE PROPER URL #

@pytest.mark.django_db
def test_studies_in_db():
    study = Study.objects.get(name='zpdes_mot')
    assert study.name == 'zpdes_mot'


# Create a general fixture to create user:
@pytest.fixture
def test_password():
    return 'test_password'


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs['password'] = test_password
        if 'username' not in kwargs:
            kwargs['username'] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)
    return make_user


@pytest.mark.django_db
def test_user_create():
    """
    Create a user and check that it is the only one in db
    :return:
    """
    User.objects.create_user('test_user', 'test_user@mail.com', 'password')
    assert User.objects.count() == 1


# Check that login page is accessible:
@pytest.mark.django_db
def test_view(client):
    """
    Check that a home view is accessible
    :key
    """
    # Rq: fixture admin_client also exists (for super user)
    url = reverse('login_page')
    response = client.get(url)
    assert response.status_code == 200


# Check that other page are not accessible:
@pytest.mark.django_db
def test_view(client):
    """
    Check that a home view is accessible
    :key
    """
    # Rq: fixture admin_client also exists (for super user)
    url = reverse('home')
    response = client.get(url)
    assert response.status_code == 302


# Own fixture for auto login:
@pytest.fixture
def auto_login_user(db, client, create_user, test_password):
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
        client.login(username=user.username, password=test_password)
        return client, user
    return make_auto_login


@pytest.mark.django_db
def test_auth_view(auto_login_user):
    """
    Check that user is able to connect
    :key
    """
    client, user = auto_login_user()
    url = reverse('login_page')
    response = client.get(url)
    assert response.status_code == 200



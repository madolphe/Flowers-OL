from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.conf import settings

from survey_app.models import Question, Answer


@login_required
@never_cache # prevents users from navigating back to this view's page without requesting it from server (i.e. by using back button)
def demo_questionnaire(request):
    print('Call to `demo_questionnaire` view in demo_app/views.py')
    return redirect(reverse('home'))
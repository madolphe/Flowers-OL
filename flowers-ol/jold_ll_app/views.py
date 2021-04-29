from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from survey_app.models import Question, Answer
from .forms import ConsentForm
from .models import JOLD_LL_trial
from manager_app.utils import add_message

import json, datetime, random



@login_required
@never_cache # prevents users from navigating back to this view's page without requesting it from server (i.e. by using back button)
def jold_start_ll_practice(request):
    """Starts a Lunar Lander practice block if not already finished"""
    participant = request.user.participantprofile
    task_name = participant.current_task.name
    # Randomly assign LL condition
    if 'game_params' not in participant.extra_json:
        participant.extra_json['game_params'] = {}
        participant.save()
    # To determine the amount of time that the block should be played for, use `setdefault`
    # If time_left key exists, use whatever value is stored. If not, use maximum time for block
    if task_name == 'jold-ll-practice':
        participant.extra_json['game_params']['forced'] = True
        participant.extra_json['game_params'].setdefault('time_left', 5 if settings.DEBUG else 5 * 60)
        participant.save()
    elif task_name == 'jold-free-choice':
        participant.extra_json['game_params']['forced'] = False
        participant.extra_json['game_params'].setdefault('time_left', 10 if settings.DEBUG else 2 * 60)
        participant.save()
    else:
        return redirect(reverse('home'))
    return render(request, 'tasks/JOLD_LL/lunar_lander.html', {'CONTEXT': {
        'game_params': json.dumps(participant.extra_json['game_params'])
    }})


def jold_save_ll_trial(request):
    """Save data from lunar lander trial"""
    participant = request.user.participantprofile
    json_string_data = list(request.POST.dict().keys()).pop()
    data = json.loads(json_string_data)
    trial = JOLD_LL_trial()
    for key, val in data.items():
        # Populate model fields with json data from POST request (keys in json object must correspond to model field keys)
        if key.startswith('_'):
            continue
        trial.__dict__[key] = val
    trial.participant = participant
    trial.session = participant.current_session
    trial.save()
    # Update remaining time
    participant.extra_json['game_params']['time_left'] = float(data['_time_left'])
    participant.save()
    return HttpResponse(status=204) # 204 is a no-content response


@login_required
@ensure_csrf_cookie
def jold_close_ll_practice(request):
    """Close lunar lander session redirect to post-sess questionnaire or the thanks page"""
    if request.is_ajax():
        participant = request.user.participantprofile
        block_complete = int(request.POST.get('blockComplete'))
        forced = int(request.POST.get('forced'))
        participant.extra_json['game_params'].pop('time_left')
        participant.save()
        # if block was completed, redirect to end task view
        if forced:
            if block_complete:
                add_message(request, _('Vous avez terminé l\'entraînement de Lunar Lander'), 'success')
                add_message(request, _('Ne partez pas tout de suite ! Il y a un questionnaire à remplir.'), 'warning')
                return JsonResponse({'success': True, 'url': reverse('end_task')})
            else:
                participant.excluded = True
                participant.save()
                return JsonResponse({'success': True, 'url': reverse('thanks_page')})
        elif not forced:
            return JsonResponse({'success': True, 'url': reverse('end_task')})


@login_required
def jold_close_postsess_questionnaire(request):
    participant = request.user.participantprofile
    add_message(request, _('Le questionnaire est complet'), 'success')
    request.session['exit_view_done'] = True
    return redirect(reverse('end_task'))


@login_required
@ensure_csrf_cookie
def jold_accept_optional_practice(request):
    return redirect(reverse('jold_free_choice', kwargs={'choice': 1}))


@login_required
@ensure_csrf_cookie
def jold_reject_optional_practice(request):
    return redirect(reverse('jold_free_choice', kwargs={'choice': 0}))


@login_required
@ensure_csrf_cookie
def jold_free_choice(request, choice):
    participant = request.user.participantprofile
    answer = Answer()
    answer.participant = participant
    answer.session = participant.current_session
    answer.question = Question.objects.get(handle='jold-0')
    answer.value = choice
    answer.save()
    if choice == 1:
        return redirect(reverse('jold_start_ll_practice'))
    else:
        return redirect(reverse('end_task')) 


@login_required
def jold_consent_page(request):
    user = request.user
    participant = user.participantprofile
    form = ConsentForm(request.POST or None, request=request)
    if form.is_valid():
        participant.consent = True
        if form.cleaned_data['request_reminder']:
            participant.remind = True
            participant.email = form.cleaned_data['email']
        participant.save()
        return redirect(reverse('end_task'))
    return render(request, 'tasks/JOLD_Consent/consent_page.html', {'CONTEXT': {
        'username': user.username,
        'study': participant.study,
        'form': form}})
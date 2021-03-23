from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.conf import settings

from survey_app.models import Question, Answer
from .models import JOLD_LL_trial
from .utils import add_message

import json, datetime, random



@login_required
@never_cache # prevents users from navigating back to this view's page without requesting it from server (i.e. by using back button)
def jold_start_ll_practice(request):
    """Starts a Lunar Lander practice block if not already finished"""
    participant = request.user.participantprofile
    task_name = participant.current_task.name
    # Randomly assign LL condition
    if 'game_params' not in participant.extra_json:
        game_params = {}
        participant.extra_json['game_params'] = game_params
        participant.save()
    if task_name == 'JOLD-ll-practice':
        participant.extra_json['game_params']['forced'] = True
        participant.extra_json['game_params']['time'] = 5 * 60
        participant.save()
    elif task_name == 'JOLD-free-choice':
        participant.extra_json['game_params']['forced'] = False
        participant.extra_json['game_params']['time'] = 60 * 2
        participant.save()
    else:
        return redirect(reverse(home))
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
        trial.__dict__[key] = val
    trial.participant = participant
    trial.session = participant.current_session
    trial.save()
    return HttpResponse(status=204) # 204 is a no-content response


@login_required
@ensure_csrf_cookie
def jold_close_ll_practice(request):
    """Close lunar lander session redirect to post-sess questionnaire or the thanks page"""
    if request.is_ajax():
        participant = request.user.participantprofile
        block_complete = int(request.POST.get('blockComplete'))
        forced = int(request.POST.get('forced'))
        # if block was completed, redirect to end task view
        if forced:
            if block_complete:
                add_message(request, _('Vous avez terminé l\'entraînement de Lunar Lander'), 'success')
                add_message(request, _('Ne partez pas tout de suite ! Il y a un questionnaire à remplir.'), 'warning')
                return JsonResponse({'success': True, 'url': reverse('end_task')})
            else:
                return JsonResponse({'success': True, 'url': reverse('thanks_page')})
        elif not forced:
            return JsonResponse({'success': True, 'url': reverse('end_task')})


@login_required
def jold_close_postsess_questionnaire(request):
    participant = request.user.participantprofile
    if participant.future_sessions:
        nextdate = (participant.date.date() + datetime.timedelta(days=participant.future_sessions[0].day-1))
        wdays = [_('Lundi'),_('Mardi'),_('Mercredi'),_('Jeudi'),_('Vendredi'),_('Samedi'),_('Dimanche')]
        add_message(request, _('La prochaine session est le'),'{} ({})'.format(nextdate.strftime('%d/%m/%Y'), wdays[nextdate.weekday()]), 'info')
    add_message(request, _('Le questionnaire est complet'), 'success')
    answer = Answer()
    answer.question = Question.objects.get(handle='jold-0')
    answer.participant = participant
    answer.session = participant.current_session
    answer.value = 0
    answer.save()
    request.session['exit_view_done'] = True
    return redirect(reverse('end_task'))


@login_required
@ensure_csrf_cookie
def jold_free_choice(request, choice=0):
    participant = request.user.participantprofile
    question = Question.objects.get(handle='jold-0')
    answer = Answer.objects.get(participant=participant, session=participant.current_session, question=question)
    answer.participant = participant
    answer.session = participant.current_session
    answer.question = question
    answer.value = choice
    answer.save()
    if choice:
        return redirect(reverse('jold_start_ll_practice'))
    else: return redirect(reverse('end_task'))

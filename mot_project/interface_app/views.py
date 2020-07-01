from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages as django_messages
from django.urls import reverse, resolve
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView
import json, datetime, random, re
from django.utils.html import mark_safe
from .models import *
from .forms import *
from .utils import add_message
from django.db.models import Count
from .alexfuncs import assign_condition
from .sequence_manager.seq_manager import SeqManager


def login_page(request, study=''):
    if 'study' in request.session:
        study = request.session.get('study')
    if 'study' in request.GET.dict():
        study = request.GET.dict().get('study')
    valid_study_title = bool(Study.objects.filter(name=study).count())
    if valid_study_title:
        request.session['study'] = study # store 'study' extension only once per session
    error = False
    form_sign_in = SignInForm(request.POST or None)
    if form_sign_in.is_valid():
        username = form_sign_in.cleaned_data['username']
        password = form_sign_in.cleaned_data['password']
        user = authenticate(request, username=username, password=password)  # Check if datas are valid
        if user:  # if user exists
            login(request, user)  # connect user
            return redirect(reverse(home))
        else:  # show error if user not in DB
            error = True
    return render(request, 'login_page.html', {'CONTEXT': {
        'study': valid_study_title,
        'error': error,
        'form': form_sign_in
    }})


def signup_page(request):
    # First, init forms, if request is valid we can create the user
    study = Study.objects.get(name=request.session['study'])
    form_user = UserForm(request.POST or None)
    form_profile = ParticipantProfileForm(request.POST or None, initial={'study': study})
    if form_user.is_valid() and form_profile.is_valid():
        # Get extra-info for user profile:
        user = form_user.save(commit=False)
        # Use set_password in order to hash password
        user.set_password(form_user.cleaned_data['password'])
        user.save()
        form_profile.save_profile(user)
        login(request, user)
        return redirect(reverse(home))                  # Redirect to consent form
    return render(request, 'signup_page.html', {'CONTEXT': {
        'form_profile': form_profile,
        'form_user': form_user
    }})


@login_required
def consent_page(request):
    user = request.user
    participant = user.participantprofile
    study = participant.study
    greeting = "Salut, {0} !".format(user.username)
    form = ConsentForm(request.POST or None)
    if form.is_valid():
        user.first_name = request.POST['nom']
        user.last_name = request.POST['prenom']
        user.save()
        participant.consent = True
        participant.save()
        participant.assign_sessions()
        return redirect(reverse(home))
    if request.method == 'POST': person = [request.POST['nom'], request.POST['prenom']]
    return render(request, 'consent_page.html', {'CONTEXT': {
        'greeting': greeting,
        'person': [request.user.first_name.capitalize(), request.user.last_name.upper()],
        'study': study,
        'form': form} })


@login_required
@never_cache
def home(request):
    participant = request.user.participantprofile
    if not participant.consent:
        return redirect(reverse(consent_page))
    participant.set_current_session() # If there is no current session, set new session as current
    if participant.current_session: request.session['active_session'] = json.dumps(True)
    if participant.current_session and not participant.current_task: # Checks if current session is empty
        'remove current session from stack so that the next if statement is true'
        request.session['active_session'] = json.dumps(False)
    if participant.sessions.count() == 0 or participant.current_session is None:
        return redirect(reverse(joldThanks)) # Should redirect to some "off session" page
    if 'messages' in request.session:
        for tag, content in request.session['messages'].items():
            django_messages.add_message(request, getattr(django_messages, tag.upper()), content)
    return render(request, 'home_page.html', { 'CONTEXT': {'participant': participant}})


@login_required
def off_session(request):
    return render(request, 'off_session.html', {'CONTEXT': {
        'page_props': page_props,
        'greeting': greeting,
        'current_sess': current_sess} })


@login_required
def user_logout(request):
    study = request.user.participantprofile.study.name
    # if participant.current_session:
    # if current session is incomplete, warn user
    logout(request)
    return redirect(reverse('login_page', args=[study]))


@login_required
def start_task(request):
    if 'messages' in request.session:
        del request.session['messages']
    return redirect(reverse(request.user.participantprofile.current_task.view_name))


@login_required
def end_task(request):
    request.user.participantprofile.pop_task()
    return redirect(reverse(home))


@login_required
def super_home(request):
    if request.user.is_authenticated & request.user.is_superuser:
        return render(request, 'super_home_page.html')


@login_required
def visual_2d_task(request):
    # Function to be removed in the future
    """Initial call to app 2D view"""
    # When it's called for the first, pass this default dict:
    # When seq manager would be init, make id_session automatic to +1
    # Search user, find highest id_session --> +1
    parameters = {'n_targets': 3, 'n_distractors': 3, 'target_color': 'red', 'distractor_color': 'yellow',
                  'radius_min': 90, 'radius_max': 120, 'speed_min': 2, 'speed_max': 2, 'episode_number': 0,
                  'nb_target_retrieved': 0, 'nb_distract_retrieved': 0,  'id_session': 0}
    # As we don't have any seq manager, let's initialize to same parameters:
    with open('interface_app/static/JSON/parameters.json', 'w') as json_file:
        json.dump(parameters, json_file)

    with open('interface_app/static/JSON/parameters.json') as json_file:
        parameters = mark_safe(json.load(json_file))
    return render(request, 'app_2D.html', locals())


@login_required
def MOT_task(request):
    """Initial call to mot-app"""
    participant = ParticipantProfile.objects.get(user=request.user.id)
    condition = participant.condition
    participant.nb_sess_started += 1
    user_episodes = []
    # Check if any session has already been finished:
    if participant.nb_sess_finished > 0:
        # Retrieve every episodes that belong to finished session:
        user_episodes = Episode.objects.filter(participant=participant, finished_session=True)
    # When it's called for the first, pass this default dict:
    # When seq manager would be init, make id_session automatic to +1
    # Search user, find highest id_session --> +1
    parameters = {'n_targets': 3, 'n_distractors': 3, 'angle_max': 9, 'angle_min': 3,
                  'radius': 90, 'speed_min': 4, 'speed_max': 4, 'episode_number': 0,
                  'nb_target_retrieved': 0, 'nb_distract_retrieved': 0,  'id_session': 0,
                  'presentation_time': 1, 'fixation_time': 1, 'tracking_time': 10,
                  'debug': 0, 'secondary_task': 'discrimination', 'SRI_max': 2, 'RSI': 1,
                  'delta_orientation': 45, 'screen_params': 39.116, 'gaming': 1}

    # Create seq manager and put it in request
    request.session['seq_manager'] = SeqManager(condition, user_episodes)
    parameters = request.session['seq_manager'].sample_task()

    # As we don't have any seq manager, let's initialize to same parameters:
    with open('interface_app/static/JSON/parameters.json', 'w') as json_file:
        json.dump(parameters, json_file)
    with open('interface_app/static/JSON/parameters.json') as json_file:
        parameters = mark_safe(json.load(json_file))

    return render(request, 'app_MOT.html', locals())


@login_required
def visual_3d_task(request):
    return render(request, 'app_3D.html', locals())


# Django security to treat ajax requests:
@csrf_exempt
def next_episode(request):
    params = request.POST.dict()
    # Save episode and results:
    episode = Episode()
    episode.participant = request.user
    for key, val in params.items():
        if key in episode.__dict__:
            episode.__dict__[key] = val
    episode.save()
    if params['secondary_task'] != 'none':
        if params['gaming'] == 1:
            params['sec_task_results'] = eval(params['sec_task_results'])
            for res in params['sec_task_results']:
                sec_task = SecondaryTask()
                sec_task.episode = episode
                sec_task.type = params['secondary_task']
                sec_task.delta_orientation = res[0]
                sec_task.answer_duration = res[1]
                sec_task.success = res[2]
                sec_task.save()
    # Function to be removed when the seq manager will be connected:
    increase_difficulty(params)
    with open('interface_app/static/JSON/parameters.json') as json_file:
        parameters = json.load(json_file)
    return HttpResponse(json.dumps(parameters))


# Hand crafted sequence manager, to be removed :
def increase_difficulty(params):
    for key, value in params.items():
        if key != 'secondary_task' and key != 'sec_task_results':
            params[key] = float(params[key])
    params['n_targets'] += 1
    params['speed_max'] *= 1.05
    params['speed_min'] *= 1.05
    params['episode_number'] += 1
    # To be coherent with how seq manager will work:
    with open('interface_app/static/JSON/parameters.json', 'w') as json_file:
        json.dump(params, json_file)


# Django security to treat ajax requests:
@csrf_exempt
def restart_episode(request):
    params = request.POST.dict()
    # Save episode and results:
    episode = Episode()
    episode.participant = request.user
    # Same params parse correctly for python:
    for key, value in params.items():
        # Just parse everything:
        if key != 'secondary_task' and key != 'sec_task_results':
            params[key] = float(params[key])
    with open('interface_app/static/JSON/parameters.json', 'w') as json_file:
        json.dump(params, json_file)
    with open('interface_app/static/JSON/parameters.json') as json_file:
        parameters = json.load(json_file)
    return HttpResponse(json.dumps(parameters))

@login_required
@never_cache # prevents users from navigating back to this view's page without requesting it from server (i.e. by using back button)
def joldStartPracticeBlockLL(request):
    """Starts a Lunar Lander practice block if not already finished"""
    participant = request.user.participantprofile
    task_name = participant.current_task.name
    # Randomly assign LL condition
    if 'game_params' not in participant.extra_json:
        game_params = {
            'wind' : random.sample([0,2,4], 1)[0],
            'plat' : random.sample([-1,0,1], 1)[0],
            'dist' : random.randint(0,1)}
        participant.extra_json['game_params'] = game_params
        participant.save()
    if task_name == 'JOLD-ll-practice':
        participant.extra_json['game_params']['forced'] = True
        participant.extra_json['game_params']['time'] = 5
        participant.save()
    elif task_name == 'JOLD-free-choice':
        participant.extra_json['game_params']['forced'] = False
        participant.extra_json['game_params']['time'] = 5*60
        participant.save()
    else:
        return redirect(reverse(home))
    return render(request, 'tasks/JOLD_LL/lunar_lander.html', {'CONTEXT': {
        'game_params': json.dumps(participant.extra_json['game_params'])
    }})


def joldSaveTrialLL(request):
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
def joldClosePracticeBlock(request):
    """Close lunar lander session redirect to post-sess questionnaire or the thanks page"""
    if request.is_ajax():
        participant = request.user.participantprofile
        block_complete = int(request.POST.get('blockComplete'))
        forced = int(request.POST.get('forced'))
        # if block was completed, redirect to end task view
        if block_complete & forced:
            add_message(request, 'Vous avez terminé l\'entraînement de Lunar Lander', 'success')
            add_message(request, 'Ne partez pas tout de suite ! Il y a un questionnaire à remplir.', 'warning')
            return JsonResponse({'success': True, 'url': reverse('end_task')})
        else:
            return JsonResponse({'success': True, 'url': reverse('JOLD_thanks')})


@login_required
@never_cache
def joldQuestionBlock(request):
    """Construct a questionnaire block and render question groups on different pages"""
    participant = request.user.participantprofile
    if 'questions_extra' not in participant.extra_json:
        # participant.save()
        task_extra = participant.current_task.extra_json
        questions = Question.objects.filter(
            instrument__in = task_extra['instruments']
        )
        for k, v in task_extra.setdefault('exclude', {}).items():
            questions = questions.exclude(**{k: v})
        groups = [i for i in questions.values('instrument', 'group').annotate(size=Count('pk'))]
        order = {k: v for v, k in enumerate(task_extra['instruments'])}
        for d in groups:
            d['order'] = order[d['instrument']]
        groups = sorted(groups, key=lambda d: (d['order'], d['group']))
        grouped_handles = []
        for group in groups:
            grouped_handles.append(
                tuple(questions.filter(
                    instrument__exact = group['instrument'],
                    group__exact = group['group']
                ).values_list('handle', flat=True))
            )
        participant.extra_json['questions_extra'] = {'grouped_handles': grouped_handles}
        participant.extra_json['questions_extra']['ind'] = 0
        participant.save()
    questions_extra = participant.extra_json['questions_extra']
    groups = questions_extra['grouped_handles']
    ind = questions_extra['ind']
    questions = Question.objects.filter(
        handle__in = groups[ind]
    )
    form = JOLDQuestionBlockForm(questions, request.POST or None)
    if form.is_valid():
        for q in questions:
            answer = Answer()
            answer.participant = participant
            answer.session = participant.current_session
            answer.question = q
            answer.value = form.cleaned_data[q.handle]
            answer.save()
        participant.extra_json['questions_extra']['ind'] += 1
        participant.save()
        if participant.extra_json['questions_extra']['ind'] == len(groups):
            del participant.extra_json['questions_extra']
            participant.save()
            add_message(request, 'Questionnaire is complete', 'success')
            nextdate = (participant.date.date() + datetime.timedelta(days=participant.future_sessions[0].day-1))
            wdays = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
            add_message(request, 'La prochaine session est le {} ({})'.format(nextdate.strftime('%d/%m/%Y'), wdays[nextdate.weekday()]), 'info')
            answer = Answer()
            answer.question = Question.objects.get(handle='jold-0')
            answer.participant = participant
            answer.session = participant.current_session
            answer.value = 0
            answer.save()
            return redirect(reverse(end_task))
        return redirect(reverse(joldQuestionBlock))
    return render(request, 'tasks/JOLD_Questionnaire/question_block.html', {'CONTEXT': {
        'form': form,
        'current_page': groups.index(groups[ind]) + 1,
        'nb_pages': len(groups)
    }})


@login_required
@ensure_csrf_cookie
def joldEndOfSession(request, choice=0):
    participant = request.user.participantprofile
    question = Question.objects.get(handle='jold-0')
    answer = Answer.objects.get(participant=participant, session=participant.current_session, question=question)
    answer.participant = participant
    answer.session = participant.current_session
    answer.question = question
    answer.value = choice
    answer.save()
    if choice:
        return redirect(reverse(joldStartPracticeBlockLL))
    else:
        return redirect(reverse(end_task))


@login_required
def joldThanks(request):
    """Render the terminal page"""
    # check how many sessions user has completed, if insufficient, redirect to
    return render(request, 'JOLD/thanks.html', locals())

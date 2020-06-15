from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, resolve
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView
import json, datetime
from django.utils.html import mark_safe
from .models import *
from .forms import *
from .alexfuncs import assign_condition


def sign_up(request):
    # First, init forms, if request is valid we can create the user
    form_user = UserForm(request.POST or None)
    form_profile = ParticipantProfileForm(request.POST or None,
        initial={'study': Study.objects.get(name=request.session['study'])})
    if form_user.is_valid() and form_profile.is_valid():
        # Get extra-info for user profile:
        user = form_user.save(commit=False)
        # Use set_password in order to hash password
        user.set_password(form_user.cleaned_data['password'])
        user.save()
        form_profile.save_profile(user)
        assign_condition(user, form_profile.data['study'])      # Assign study conditions
        login(request, user)
        return redirect(reverse(home_user))                  # Redirect to consent form
    return render(request, 'sign_up.html', {'CONTEXT': {
        'form_profile': form_profile,
        'form_user': form_user
    } })


def home(request, study=''):
    if 'study' in request.session: study = request.session.get('study')
    if 'study' in request.GET.dict(): study = request.GET.dict().get('study')
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
            return redirect(reverse(home_user))
        else:  # show error if user not in DB
            error = True
    return render(request, 'home.html', {'CONTEXT': {
        'study': valid_study_title,
        'error': error,
        'form': form_sign_in
    }})


@login_required
def consent_page(request):
    user = request.user
    participant = user.participantprofile
    study_specs = participant.study
    greeting = "Salut, {0} !".format(user.username)
    consent_text = study_specs.consent_text
    project = study_specs.project
    form = ConsentForm(request.POST or None)
    if form.is_valid():
        user.first_name = request.POST['nom']
        user.last_name = request.POST['prenom']
        user.save()
        participant.consent = True
        participant.save()
        spacing = study_specs.spacing.strip('[]').split(',')
        if study_specs.nb_sessions > len(spacing):
            spacing += [spacing[0] for s in range(study_specs.nb_sessions)]
        for i, day_delta in enumerate(spacing):
            session = ExperimentSession()
            session.participant = participant
            session.date = datetime.date.today() + datetime.timedelta(days=int(day_delta))
            session.num = i+1
            session.save()
        return redirect(reverse(home_user))
    if request.method == 'POST': person = [request.POST['nom'], request.POST['prenom']]
    return render(request, 'consent_form.html', {'CONTEXT': {
        'greeting': greeting,
        'person': [request.user.first_name.capitalize(), request.user.last_name.upper()],
        'study_specs': study_specs,
        'form': form} })


@login_required
def home_user(request):
    if request.user.is_authenticated:
        participant = request.user.participantprofile
        if request.user.is_superuser:
            return render(request, 'home_superuser.html')
        if not participant.consent:
            return redirect(reverse(consent_page))
        study_specs = participant.study
        greeting = "Salut, {0} !".format(request.user.username)
        sess_num = ExperimentSession.objects.get(participant=participant, date=datetime.date.today()).num
    return render(request, 'home_user.html', {'CONTEXT': {
        'page_props':page_props,
        'greeting': greeting,
        'current_sess': current_sess} })


@login_required
def user_logout(request):
    study = request.user.participantprofile.study.name
    if request.user.is_authenticated:
        logout(request)
        return redirect(reverse('home', args=[study]))


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
    """Initial call to app 2D view"""
    # When it's called for the first, pass this default dict:
    # When seq manager would be init, make id_session automatic to +1
    # Search user, find highest id_session --> +1
    parameters = {'n_targets': 3, 'n_distractors': 3, 'angle_max': 9, 'angle_min': 3,
                  'radius': 90, 'speed_min': 4, 'speed_max': 4, 'episode_number': 0,
                  'nb_target_retrieved': 0, 'nb_distract_retrieved': 0,  'id_session': 0,
                  'presentation_time': 1, 'fixation_time': 1, 'tracking_time': 10,
                  'debug': 0, 'secondary_task': 'discrimination', 'SRI_max': 2, 'RSI': 1,
                  'delta_orientation': 45, 'screen_params': 39.116, 'gaming': 1}
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
def joldStartPracticeBlockLL(request, forced=True):
    """Start a Lunar Lander practice block if not finished"""
    if not request.user.is_superuser:
        participant = request.user.participantprofile
        if ExperimentSession.objects.get(participant=participant, date=datetime.date.today()).practice_finished:
            return redirect(reverse(request.session['checkpoint']['url'], args=request.session['checkpoint']['args']))
        participant.nb_practice_blocks_started += int(forced)
        participant.save()
        xparams = { # make sure to keep difficulty constant for the same participant!
            'wind': participant.wind,
            'plat': participant.plat,
            'dist': participant.dist,
            'time': 2 if bool(forced) else 5*60,
            'forced': bool(forced),
        }
    else:
        xparams = { # make sure to keep difficulty constant for the same participant!
            'wind': "0",
            'plat': "0",
            'dist': "2",
            'time': "5",
        }
    xparams = json.dumps(xparams)
    return render(request, 'JOLD/lunar_lander.html', {'XPARAMS': xparams})


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
    trial.session = ExperimentSession.objects.get(participant=participant, date=datetime.date.today())
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
        # if session complete, redirect to transition to post-sess Q&A
        if block_complete & forced:
            participant.nb_practice_blocks_finished += 1
            participant.save()
            session = ExperimentSession.objects.get(participant=participant, date=datetime.date.today())
            session.practice_finished = True
            session.save()
            return JsonResponse({'success': True, 'url': reverse('JOLD_transition')})
        else:
            return JsonResponse({'success': True, 'url': reverse('JOLD_thanks')})


@login_required
def joldTransition(request):
    request.session['checkpoint'] = {'url':'JOLD_transition', 'args': None}
    participant = request.user.participantprofile
    study_specs = participant.study
    session = ExperimentSession.objects.get(participant=participant, date=datetime.date.today())
    return render(request, 'JOLD/transition.html', {'CONTEXT': {
        'current_sess': session.num, 'study_specs': study_specs
    }})


@never_cache
def joldQuestionBlock(request, num=0):
    """Construct a questionnaire block and render question groups on different pages"""
    request.session['checkpoint'] = {'url':'JOLD_question_block', 'args': [num]}
    participant = request.user.participantprofile
    session = ExperimentSession.objects.get(participant=participant, date=datetime.date.today())
    questions = Question.objects.filter(session_list__regex='(^|,|\[){}(,|$|\])'.format(session.num))
    groups = sorted(list(questions.values_list('group', flat=True).distinct()))
    questions = questions.filter(group__exact=groups[num]).order_by('order')
    form = JOLDQuestionBlockForm(questions, num, request.POST or None)
    if form.is_valid():
        for q in questions:
            answer = Answer()
            answer.participant = participant
            answer.session = session
            answer.question = q
            answer.value = form.cleaned_data[q.handle]
            answer.save()
        if form.index == len(groups) - 1:
            participant.nb_question_blocks_finished += 1
            participant.save()
            session.questions_finished = True
            session.save()
            return redirect(reverse(joldEndOfSession))
        return redirect('JOLD_question_block', num=num+1)
    else:
        context = {'FORM': form, 'STAGE': num+1, 'NSTAGES': len(groups)}
        return render(request, 'JOLD/question_block.html', context)


@login_required
@ensure_csrf_cookie
def joldEndOfSession(request):
    request.session['checkpoint'] = {'url':'JOLD_end_of_session', 'args': None}
    participant = request.user.participantprofile
    session = ExperimentSession.objects.get(participant=participant, date=datetime.date.today())
    answer = Answer()
    answer.participant = participant
    answer.sess = session
    answer.question = Question.objects.get(handle='jold-0')
    if request.method == 'POST':
        choice = int(request.POST.dict().get('choice'))
        answer.value = choice
        answer.save()
        url = 'JOLD_start_practice_block_ll' if choice==1 else 'JOLD_thanks'
        args = [0] if choice else None
        return JsonResponse({'success': True, 'url': reverse(url, args=args)})
    answer.value = 0
    answer.save()
    study_specs = participant.study
    tasks = [session.practice_finished]
    if session.questions_finished is not None: tasks.append(session.questions_finished)
    session.is_finished = all(tasks)
    session.save()
    return render(request, 'JOLD/free_choice.html', {'CONTEXT': {
        'current_sess': session.num,
        'study_specs': study_specs }})


@login_required
def joldThanks(request):
    """Render the terminal page"""
    # check how many sessions user has completed, if insufficient, redirect to
    return render(request, 'JOLD/thanks.html', locals())


from django.shortcuts import render, redirect, HttpResponse
from .forms import UserForm, ParticipantProfileForm, SignInForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.html import mark_safe
from .models import Episode, JOLD_trial_LL, JOLD_params_LL, SecondaryTask
from .alexfuncs import assign_condition


def sign_up(request):
    # First, init forms, if request is valid we can create the user
    form_user = UserForm(request.POST or None)
    study = request.META['HTTP_REFERER'].split('/')[-1] # either jold_ll, jold_mot, or zpdes_mot
    form_profile = ParticipantProfileForm(request.POST or None, initial={'study': study})
    if form_user.is_valid() and form_profile.is_valid():
        # Get extra-info for user profile:
        user = form_user.save(commit=False)
        # Use set_password in order to hash password
        user.set_password(form_user.cleaned_data['password'])
        user.save()
        form_profile.save_profile(user)
        assign_condition(user, form_profile.data['study']) # Assign experimental condition to user
        login(request, user) # Redirect to user homepage
        return redirect(reverse(home_user))
    context = {'form_profile': form_profile, 'form_user': form_user}
    return render(request, 'sign_up.html', context)


def home(request):
    # First, init forms, if request is valid we check if the user exists
    # print(request)
    error = False
    form_sign_in = SignInForm(request.POST or None)
    if form_sign_in.is_valid():
        username = form_sign_in.cleaned_data['username']
        password = form_sign_in.cleaned_data['password']
        user = authenticate(request, username=username, password=password)  # Check if datas are valid
        if user:  # if user exists
            login(request, user)  # connect user
            return redirect(reverse(home_user))
        else:  # sinon une erreur sera affichée
            error = True
    return render(request, 'home.html', locals())


@login_required
def home_user(request):
    if request.user.is_authenticated:
        study = request.user.participantprofile.study
        context = "Salut, {0} !".format(request.user.username)
    return render(request, 'home_user.html', locals())


@login_required
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(reverse(home))


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
                  'delta_orientation': 45, 'screen_params': 39.116}
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
    params['speed_max'] *= 1.2
    params['speed_min'] *= 1.2
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


# view for requested Lunar Lander session (i.e. practice block)
@login_required
def joldStartSess_LL(request):
    """Call to Lunar Lander view"""
    user_params = JOLD_params_LL.objects.get(participant_id=request.user.id)
    xparams = { # make sure to keep difficulty constant for the same participant!
        'wind': user_params.wind,
        'plat': user_params.plat,
        'dist': user_params.dist
    }
    # Initialize game same parameters:
    with open('interface_app/static/JSON/LL_params.json', 'w') as json_file:
        json.dump(xparams, json_file)

    with open('interface_app/static/JSON/LL_params.json') as json_file:
        xparams = mark_safe(json.load(json_file))
    return render(request, 'app_LL.html', locals())


@csrf_exempt
def joldSaveTrial_LL(request):
    json_string_data = list(request.POST.dict().keys()).pop()
    data = json.loads(json_string_data)
    table = JOLD_trial_LL()
    for key, val in data.items():
        table.__dict__[key] = val
    table.participant = request.user
    table.save()
    return HttpResponse(status=204) # 204 is a no-content response

# @TODO: print number of episode restant
# @TODO: print score
# @TODO: test new design for frontend
# @TODO: refacto code --> mainly js + comments

from django.shortcuts import render, redirect, HttpResponse
from .forms import UserForm, ParticipantProfileForm, SignInForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.html import mark_safe
from .models import Episode


def sign_up(request):
    # First, init forms, if request is valid we can create the user
    form_user = UserForm(request.POST or None)
    form_profile = ParticipantProfileForm(request.POST or None)
    if form_user.is_valid() and form_profile.is_valid():
        # Get extra-info for user profile:
        user = form_user.save(commit=False)
        # Use set_password in order to hash password
        user.set_password(form_user.cleaned_data['password'])
        user.save()
        form_profile.save_profile(user)
        # Redirect to user homepage:
        login(request, user)
        return redirect(reverse(home_user))
    context = {'form_profile': form_profile, 'form_user': form_user}
    return render(request, 'sign_up.html', context)


def home(request):
    # First, init forms, if request is valid we check if the user exists
    print(request)
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
        context = "Salut, {0} !".format(request.user.username)
    return render(request, 'home_user.html', locals())


@login_required
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(reverse(home))


@login_required
def visual_2d_task(request):
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
                  'presentation_time': 1000, 'fixation_time': 1000, 'tracking_time': 12000,
                  'debug': 0, 'secondary_task': 'detection'}
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
    print(params)
    score = '['+str(params['nb_target_retrieved'])+','+str(params['nb_distract_retrieved'])+']'
    episode.score = score
    episode.id_session = params['id_session']
    episode.save()
    # Function to be removed when the seq manager will be connected:
    increase_difficulty(params)
    with open('interface_app/static/JSON/parameters.json') as json_file:
        parameters = json.load(json_file)
    return HttpResponse(json.dumps(parameters))


# Hand crafted sequence manager:
def increase_difficulty(params):
    params['n_targets'] = int(params['n_targets']) + 1
    params['speed_max'] = int(params['speed_max']) + 1
    params['speed_min'] = int(params['speed_min']) + 1
    params['episode_number'] = int(params['episode_number']) + 1
    params['n_distractors'] = int(params['n_distractors'])
    params['radius'] = int(params['radius'])
    params['presentation_time'] = int(params['presentation_time'])
    params['fixation_time'] = int(params['fixation_time'])
    params['tracking_time'] = int(params['tracking_time'])
    params['angle_max'] = int(params['angle_max'])
    params['angle_min'] = int(params['angle_min'])
    params['id_session'] = int(params['id_session'])
    params['nb_target_retrieved'] = int(params['nb_target_retrieved'])
    params['nb_distract_retrieved'] = int(params['nb_distract_retrieved'])
    params['debug'] = int(params['debug'])
    # To be coherent with how seq manager will work:
    with open('interface_app/static/JSON/parameters.json', 'w') as json_file:
        json.dump(params, json_file)

from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, resolve
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView
import json
from django.utils.html import mark_safe
from .models import *
from .forms import *
from .alexfuncs import assign_condition


def sign_up(request):
    # First, init forms, if request is valid we can create the user
    form_user = UserForm(request.POST or None)
    form_profile = ParticipantProfileForm(request.POST or None, initial={'study': request.session['study']})
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
    context = {'form_profile': form_profile, 'form_user': form_user}
    return render(request, 'sign_up.html', context)


def home(request):
    # First, init forms, if request is valid we check if the user exists
    extension = resolve(request.path_info).url_name.strip('home').strip('-')
    if extension: request.session['study'] = extension # store 'study' extension only once
    NO_EXT = 1 if 'study' not in request.session else 0

    ERROR = False
    form_sign_in = SignInForm(request.POST or None)
    if form_sign_in.is_valid():
        username = form_sign_in.cleaned_data['username']
        password = form_sign_in.cleaned_data['password']
        user = authenticate(request, username=username, password=password)  # Check if datas are valid
        if user:  # if user exists
            login(request, user)  # connect user
            return redirect(reverse(home_user))
        else:  # sinon une erreur sera affichée
            ERROR = True
    return render(request, 'home.html', locals())


@login_required
def consent_page(request):
    # First, identify user id and study
    participant = ParticipantProfile.objects.get(user=request.user.id)
    study = participant.study
    person = [request.user.first_name.capitalize(), request.user.last_name.upper()]
    greeting = "Salut, {0} !".format(request.user.username)
    # Depending on study, consent_form could be different:
    # Look for correct datas in DynamicProps model:
    consent_text = DynamicProps.objects.get(study=study).consent_text
    project = DynamicProps.objects.get(study=study).project
    # Check for form validation:
    form = ConsentForm(request.POST or None)
    if form.is_valid():
        request.user.first_name = request.POST['nom']
        request.user.last_name = request.POST['prenom']
        request.user.save()
        participant.consent = True
        participant.save()
        return redirect(reverse(home_user))
    # Form is not valid yet:
    # A way to get participant name/firstname is to use django current request
    # (thank to @login_required)
    if request.method == 'POST':
        person = [request.POST['nom'], request.POST['prenom']]
    context = {
        'FORM': form, 'GREETING': greeting,
        'TEXT': consent_text, 'PERSON': person, 'PROJECT': project}
    return render(request, 'consent_form.html', context)

@login_required
def get_profil(request):
    participant = ParticipantProfile.objects.get(user=request.user.id)
    study = participant.study
    



@login_required
def home_user(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, 'home_superuser.html', locals())
        elif not ParticipantProfile.objects.get(user=request.user.id).consent:
            return redirect(reverse(consent_page))
        elif ParticipantProfile.objects.get(user=request.user.id).study == 'zpdes_mot':
            return redirect(reverse(get_profil))
        study = request.user.participantprofile.study
        PAGE_PROPS = DynamicProps.objects.get(study=study)
        GREETING = "Salut, {0} !".format(request.user.username)
        CURRENT_SESS = request.user.participantprofile.nb_sess_finished + 1
    return render(request, 'home_user.html', locals())


@login_required
def user_logout(request):
    # TODO check if user exists before showing the warning message!!
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


# Start a Lunar Lander session
@login_required
def joldStartSess_LL(request, forced=True):
    """Call to Lunar Lander view"""
    if not request.user.is_superuser:
        participant = ParticipantProfile.objects.get(user=request.user.id)
        participant.nb_sess_started += 1
        participant.save()
        xparams = { # make sure to keep difficulty constant for the same participant!
            'wind': participant.wind,
            'plat': participant.plat,
            'dist': participant.dist,
            'time': 10 if bool(forced) else 5*60,
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


# Save data from lunar lander trial
def joldSaveTrial_LL(request):
    participant = ParticipantProfile.objects.get(user=request.user.id)
    json_string_data = list(request.POST.dict().keys()).pop()
    data = json.loads(json_string_data)
    table = JOLD_LL_trial()
    for key, val in data.items():
        table.__dict__[key] = val
    table.participant = participant
    table.sess_number = participant.nb_sess_started
    table.save()
    return HttpResponse(status=204) # 204 is a no-content response


# Close lunar lander session redirect to post-sess questionnaire or the thanks page
@login_required
@ensure_csrf_cookie
def joldEndSess(request):
    if request.is_ajax():
        participant = ParticipantProfile.objects.get(user=request.user.id)
        session_complete = int(request.POST.get('sessComplete'))
        forced = int(request.POST.get('forced'))
        # if session complete, redirect to transition to post-sess Q&A
        if session_complete & forced:
            participant.nb_sess_finished += 1
            participant.save()
            return JsonResponse({'success': True, 'url': reverse('JOLD_transition')})
        else:
            return JsonResponse({'success': True, 'url': reverse('JOLD_thanks')})


@login_required
def joldTransition(request):
    page_props = DynamicProps.objects.get(study=request.user.participantprofile.study)
    current_sess = request.user.participantprofile.nb_sess_finished
    return render(request, 'JOLD/transition.html', {'CURRENT_SESS': current_sess, 'PAGE_PROPS': page_props})


# Construct a post-sess questionnaire and render question groups on different pages
@never_cache
def joldPostSess(request, num=0):
    participant = ParticipantProfile.objects.get(user=request.user.id)
    sess = participant.nb_sess_finished
    questions = QBank.objects.filter(sessions__regex='(^|,){}(,|$)'.format(sess))
    groups = questions.values_list('group', flat=True).distinct()
    questions = questions.filter(group__exact=groups[num])
    form = JOLDPostSessForm(questions, num, request.POST or None)
    if form.is_valid():
        for q in questions:
            r = Responses()
            r.participant = participant
            r.sess = sess
            r.question = q
            r.answer = form.cleaned_data[q.handle]
            r.save()
        if form.index == len(groups) - 1:
            participant.nb_followups_finished += 1
            participant.save()
            return redirect(reverse(joldFreeChoice))
        return redirect('JOLD_post_sess', num=num+1)
    else:
        context = {'FORM': form, 'STAGE': num+1, 'NSTAGES': len(groups)}
        return render(request, 'JOLD/post_sess.html', context)


@login_required
def joldFreeChoice(request):
    if request.user.is_authenticated:
        page_props = DynamicProps.objects.get(study=request.user.participantprofile.study)
        current_sess = request.user.participantprofile.nb_sess_finished
        return render(request, 'JOLD/free_choice.html', {'CURRENT_SESS': current_sess, 'PAGE_PROPS': page_props})


# Render the terminal page
@login_required
def joldThanks(request):
    participant = ParticipantProfile.objects.get(user=request.user.id)
    participant.nb_sess_finished
    # check how many sessions user has completed, if insufficient, redirect to
    return render(request, 'JOLD/thanks.html', locals())

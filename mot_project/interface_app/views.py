from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages as django_messages
from django.urls import reverse, resolve
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.cache import never_cache
import json, datetime, random, re
from .models import *
from .forms import *
from .utils import add_message, assign_mot_condition
from django.db.models import Count
from .sequence_manager.seq_manager import MotParamsWrapper
import kidlearn_lib as k_lib
from kidlearn_lib import functions as func
from django.conf import settings

# @TODO: play and make seq manager work (sampling/remaining episode/nb_targets_retrieved transition)
# @TODO: Display episodes in home with new template
# @TODO: add probe duration to gaming dynamic


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
    if not participant.consent: return redirect(reverse(consent_page))
    try: participant.set_current_session()
    except AssertionError: return redirect(reverse(thanks_page))
    if not participant.current_session_valid:
        return redirect(reverse(off_session_page))
    if participant.current_session:
         request.session['active_session'] = json.dumps(True)
    if 'messages' in request.session:
        for tag, content in request.session['messages'].items():
            django_messages.add_message(request, getattr(django_messages, tag.upper()), content)
    return render(request, 'home_page.html', { 'CONTEXT': {'participant': participant}})


@login_required
def off_session_page(request):
    participant = request.user.participantprofile
    day1 = participant.date.date()
    schedule, status = [], 1
    for s in ExperimentSession.objects.filter(study=participant.study):
        date = day1 + datetime.timedelta(days=s.day-1)
        sdate = date.strftime('%d/%m/%Y')
        if participant.current_session == s:
            status = 0
        schedule.append([sdate, status])
    return render(request, 'off_session_page.html', {'CONTEXT': {
        'schedule': schedule}})


@login_required
def thanks_page(request):
    participant = request.user.participantprofile
    if participant.sessions.count():
        heading = 'La session est terminée'
        session_day = participant.sessions.first().day
        if session_day:
            next_date = participant.date.date() + datetime.timedelta(days=session_day-1)
            text = 'Nous vous attendons la prochaine fois. Votre prochaine session est le {}'.format(next_date.strftime('%d/%m/%Y'))
        else:
            text = 'Nous vous attendons la prochaine fois.'
    else:
        heading = 'L\'étude est terminée'
        text = 'Merci, pour votre contribution à la science !'
    return render(request, 'thanks_page.html', {'CONTEXT': {
        'heading': heading, 'text': text}})


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
    ''' A task exit_view function must change the 'exit_view_done' field of the request.session dict to True,
    in order to be run just once. The exit_view must also redirect back to this view. '''

    participant = request.user.participantprofile
    if participant.current_task.exit_view and not request.session.setdefault('exit_view_done', False):
        print('Redirecting to exit view: {}'.format(participant.current_task.exit_view))
        return redirect(reverse(participant.current_task.exit_view))
    if 'exit_view_done' in request.session: del request.session['exit_view_done']
    participant.pop_task()
    # Check if current session is empty
    if participant.current_session and not participant.current_task:
        return redirect(reverse(end_session))
    return redirect(reverse(home))


@login_required
def end_session(request):
    participant = request.user.participantprofile
    participant.close_current_session()
    request.session['active_session'] = json.dumps(False)
    participant.queue_reminder()
    return redirect(reverse(thanks_page))


@login_required
def super_home(request):
    if request.user.is_authenticated & request.user.is_superuser:
        return render(request, 'super_home_page.html')


@login_required
@csrf_exempt
def set_mot_params(request):
    participant = request.user.participantprofile
    # Case 1: user comes from home and has modified his screen params:
    if "screen_params_input" in request.POST.dict():
        add_message(request, "Paramètres d'écran modifiés.")
        participant.extra_json['screen_params'] = request.POST['screen_params_input']
        participant.save()
        # update screen params and return home:
        return redirect(reverse(home))
    else:
        # Case 2: user has just applied and provide screen params for the first time:
        # Normaly current task should be retrieving screen_params:
        instrument = participant.current_task.extra_json['instruments']
        handle = participant.current_task.extra_json['include']['handle__in'][0]
        # Warning here it works because of only one handle
        questions = Question.objects.filter(instrument__in=instrument)
        q = questions.get(handle=handle)
        form = JOLDQuestionBlockForm([q], request.POST or None)
        if form.is_valid():
            answer = Answer()
            answer.participant = participant
            answer.session = participant.current_session
            answer.question = q
            answer.value = form.cleaned_data[q.handle]
            answer.save()
            # The line I really need is here:
            participant.extra_json['screen_params'] = form.cleaned_data[q.handle]
            participant.save()
            return redirect(reverse(end_task))
        return render(request, 'tasks/JOLD_Questionnaire/question_block.html', {'CONTEXT': {
            'form': form,
            'current_page': 1,
            'nb_pages': 1}})


@login_required
def MOT_task(request):
    """Initial call to mot-app"""
    # Var to placed in a config file :
    dir_path = "interface_app/static/JSON/config_files"
    # Get participant :
    participant = ParticipantProfile.objects.get(user=request.user.id)
    # Init a wrapper for mot :
    mot_wrapper = MotParamsWrapper(participant)
    if "condition" not in participant.extra_json:
        # Participant hasn't been put in a group:
        assign_mot_condition(participant)
    # Init the correct sequence manager:
    if participant.extra_json['condition'] == 'zpdes':
        zpdes_params = func.load_json(file_name='ZPDES_mot', dir_path=dir_path)
        request.session['seq_manager'] = k_lib.seq_manager.ZpdesHssbg(zpdes_params)
    else:
        mot_baseline_params = func.load_json(file_name="mot_baseline_params", dir_path=dir_path)
        request.session['seq_manager'] = k_lib.seq_manager.MotBaselineSequence(mot_baseline_params)
    # If this is not the first time the user plays, build his history :
    history = Episode.objects.filter(participant=request.user)
    for episode in history:
        request.session['seq_manager'] = mot_wrapper.update(episode, request.session['seq_manager'])
    request.session['mot_wrapper'] = mot_wrapper
    # Get parameters for task:
    parameters = mot_wrapper.sample_task(request.session['seq_manager'])
    # Serialize it to pass it to js_mot:
    parameters = json.dumps(parameters)
    return render(request, 'app_MOT.html', {'CONTEXT': {'parameter_dict': parameters}})


@login_required
@csrf_exempt
def next_episode(request):
    mot_wrapper = request.session['mot_wrapper']
    params = request.POST.dict()
    # Save episode and results:
    episode = Episode()
    episode.participant = request.user
    for key, val in params.items():
        if key in episode.__dict__:
            episode.__dict__[key] = val
    episode.save()
    # In case of secondary task:
    if params['secondary_task'] != 'none' and params['gaming'] == 1:
        params['sec_task_results'] = eval(params['sec_task_results'])
        for res in params['sec_task_results']:
            sec_task = SecondaryTask()
            sec_task.episode = episode
            sec_task.type = params['secondary_task']
            sec_task.delta_orientation = res[0]
            sec_task.answer_duration = res[1]
            sec_task.success = res[2]
            sec_task.save()
    seq_param = request.session['seq_manager']
    seq_param = mot_wrapper.update(episode, seq_param)
    parameters = mot_wrapper.sample_task(seq_param)
    request.session['seq_manager'] = seq_param
    return HttpResponse(json.dumps(parameters))


@login_required
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
def jold_start_ll_practice(request):
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
        participant.extra_json['game_params']['time'] = 5 if settings.DEBUG else 60 * 5
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
                add_message(request, 'Vous avez terminé l\'entraînement de Lunar Lander', 'success')
                add_message(request, 'Ne partez pas tout de suite ! Il y a un questionnaire à remplir.', 'warning')
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
        wdays = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
        add_message(request, 'La prochaine session est le {} ({})'.format(nextdate.strftime('%d/%m/%Y'), wdays[nextdate.weekday()]), 'info')
    answer = Answer()
    answer.question = Question.objects.get(handle='jold-0')
    answer.participant = participant
    answer.session = participant.current_session
    answer.value = 0
    answer.save()
    request.session['exit_view_done'] = True
    return redirect(reverse(end_task))


@login_required
@never_cache
def joldQuestionBlock(request):
    """Construct a questionnaire block and render question groups on different pages"""
    participant = request.user.participantprofile
    if 'questions_extra' not in participant.extra_json:
        task_extra = participant.current_task.extra_json
        questions = Question.objects.filter(
            instrument__in = task_extra['instruments']
        )
        for k, v in task_extra.setdefault('exclude', {}).items():
            questions = questions.exclude(**{k: v})
        groups = [i for i in questions.values('instrument', 'group').annotate(size=Count('handle'))]
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
            return redirect(reverse(end_task))
        return redirect(reverse(joldQuestionBlock))
    return render(request, 'tasks/JOLD_Questionnaire/question_block.html', {'CONTEXT': {
        'form': form,
        'current_page': groups.index(groups[ind]) + 1,
        'nb_pages': len(groups)
    }})


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
        return redirect(reverse(jold_start_ll_practice))
    else:
        return redirect(reverse(end_task))

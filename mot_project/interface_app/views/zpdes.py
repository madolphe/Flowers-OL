from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse, resolve
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from ..models import Question, SecondaryTask, Episode, Answer, ParticipantProfile
from ..forms import QuestionnaireForm
from ..utils import add_message, assign_mot_condition
from ..sequence_manager.seq_manager import MotParamsWrapper

from collections import defaultdict
import json, datetime

import kidlearn_lib as k_lib
from kidlearn_lib import functions as func


@login_required
def mot_close_task(request):
    participant = request.user.participantprofile
    params = request.POST.dict()
    game_end = False
    # Game is over:
    if params['game_end'] == 'true':
        game_end = True
    if not game_end:
        min = int(request.POST.dict()['game_time']) // 60
        sec = int(request.POST.dict()['game_time']) - (min * 60)
        request.session['mot_wrapper'].set_parameter('game_time', request.POST.dict()['game_time'])
        add_message(request, 'Il vous reste encore du temps de jeu: {} min et {} sec, continuez!'.format(min, sec),
                    tag='WARNING')
        # Store that participant just paused the game:
        participant.extra_json['paused_mot_start'] = str(datetime.time)
        participant.extra_json['game_time_to_end'] = request.POST.dict()['game_time']
        participant.save()
        return redirect(reverse('home'))
    else:
        # If mot close and time is over, just remove game_time_to_end:
        if 'game_time_to_end' in participant.extra_json:
            del participant.extra_json['game_time_to_end']
            participant.save()
        add_message(request, 'Vous avez terminé la session de jeu!', 'success')
        request.session['exit_view_done'] = True
        return redirect(reverse('end_task'))


@login_required
@csrf_exempt
def set_mot_params(request):
    participant = request.user.participantprofile
    # Case 1: user comes from home and has modified his screen params:
    if "screen_params_input" in request.POST.dict():
        try:
            float(request.POST['screen_params_input'])
            add_message(request, "Paramètres d'écran modifiés.")
            # use extra_json for prompt in view and save it:
            participant.extra_json['screen_params'] = request.POST['screen_params_input']
            participant.save()
            # also update answer:
            answers = Answer.objects.filter(participant=participant)
            answer = answers.get(question__handle='prof-1')
            answer.value = request.POST['screen_params_input']
            answer.save()
            # update screen params and return home:
        except ValueError:
            add_message(request, "Fournir une valeur réelle svp (ex: 39.116).", tag="error")
        return redirect(reverse('home'))
    else:
        # Case 2: user has just applied and provide screen params for the first time:
        # Normaly current task should be retrieving screen_params:
        instrument = participant.current_task.extra_json['instruments']
        handle = participant.current_task.extra_json['include']['handle__in'][0]
        # Warning here it works because of only one handle
        questions = Question.objects.filter(instrument__in=instrument)
        q = questions.get(handle=handle)
        form = QuestionnaireForm([q], request.POST or None)
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
            return redirect(reverse('end_task'))
        return render(request, 'tasks/JOLD_Questionnaire/question_block.html', {'CONTEXT': {
            'form': form,
            'current_page': 1,
            'nb_pages': 1}})


@login_required
def MOT_task(request):
    """
    View called when button "begin task" is selected.
    :param request:
    :return:
    """
    # Var to placed in a config file :
    dir_path = "interface_app/static/JSON/config_files"
    # Get participant :
    participant = ParticipantProfile.objects.get(user=request.user.id)
    # First assign condition if first connexion:
    if "condition" not in participant.extra_json:
        # Participant hasn't been put in a group:
        assign_mot_condition(participant)
    # Set new mot_wrapper (erase old one if exists):
    request.session['mot_wrapper'] = MotParamsWrapper(participant)
    if 'game_time_to_end' in participant.extra_json:
        # If players has already played / reload page (and delete cache) for this session, game_time has to be set:
        request.session['mot_wrapper'].parameters['game_time'] = int(participant.extra_json['game_time_to_end'])
    # Set new sequence_manager (erase the previous one if exists):
    if participant.extra_json['condition'] == 'zpdes':
        zpdes_params = func.load_json(file_name='ZPDES_mot', dir_path=dir_path)
        request.session['seq_manager'] = k_lib.seq_manager.ZpdesHssbg(zpdes_params)
    else:
        mot_baseline_params = func.load_json(file_name="mot_baseline_params", dir_path=dir_path)
        request.session['seq_manager'] = k_lib.seq_manager.MotBaselineSequence(mot_baseline_params)
    # Build his history :
    history = Episode.objects.filter(participant=request.user)
    for episode in history:
        # Call mot_wrapper to parse django episodes and update seq_manager
        request.session['seq_manager'] = request.session['mot_wrapper'].update(episode, request.session['seq_manager'])
    # Get parameters for task:
    parameters = request.session['mot_wrapper'].sample_task(request.session['seq_manager'])
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
    # In case the user reloads page, we save in participant extra_json the game_time_to_end:
    participant = request.user.participantprofile
    participant.extra_json['game_time_to_end'] = request.POST.dict()['game_time']
    participant.save()
    # Sample new episode:
    request.session['seq_manager'] = mot_wrapper.update(episode, request.session['seq_manager'])
    parameters = mot_wrapper.sample_task(request.session['seq_manager'])
    return HttpResponse(json.dumps(parameters))


@login_required
@csrf_exempt
def restart_episode(request):
    parameters = request.POST.dict()
    # Save episode and results:
    episode = Episode()
    episode.participant = request.user
    # Same params parse correctly for python:
    for key, value in parameters.items():
        # Just parse everything:
        try:
            parameters[key] = float(value)
        except ValueError:
            parameters[key] = value
    return HttpResponse(json.dumps(parameters))


@login_required
def display_progression(request):
    participant = request.user.participantprofile
    # Retrieve all played episodes:
    history = Episode.objects.filter(participant=request.user)
    display_fields = ['n_targets', 'n_distractors', 'speed_max', 'tracking_time', 'probe_time']
    CONTEXT = defaultdict(list)
    for episode in history:
        for field in display_fields:
            CONTEXT[episode.id].append(episode.__dict__[field])
        CONTEXT[episode.id].append(episode.get_results)
    CONTEXT = dict(CONTEXT)
    participant.extra_json['history'] = CONTEXT
    return render(request, 'tasks/ZPDES_mot/display_progression.html',
                  {'CONTEXT': {'participant': participant}})

from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from .models import SecondaryTask, Episode
from manager_app.models import ParticipantProfile
from survey_app.models import Question, Answer
from survey_app.forms import QuestionnaireForm
from \
    manager_app.utils import add_message
from .utils import assign_mot_condition
from .sequence_manager.seq_manager import MotParamsWrapper
from .models import CognitiveTask, CognitiveResult

from collections import defaultdict
import json
import datetime
import random

import kidlearn_lib as k_lib
from kidlearn_lib import functions as func

# ### Views and utilities for mot_app-task ###
NUMBER_OF_TASKS_PER_BATCH = 2


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
            print(participant.extra_json)
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
    dir_path = "static/JSON/config_files"
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
    return render(request, 'mot_app/app_MOT.html', {'CONTEXT': {'parameter_dict': parameters}})


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
    return render(request, 'mot_app/display_progression.html',
                  {'CONTEXT': {'participant': participant}})


# ### Views and utilities for pre-post-task ###

@login_required
@never_cache
def cognitive_assessment_home(request):
    """
    This view is the controller for the all activity. It checks the current status of the pre/post test.
    5 possibilities:
    1) This is the first activity for the participant:
        - Create a task stack (random)
        - Update status (pre/post - phase1)
        - Launch the first activity
    2) There is an another activity in the task stack:
        - Save last activity results
        - Launch the next activity
    3) This is the break
        - Save last activity results
        - Exit this view and call to 'end-task' view
    4) This is the first activity after the break:
        - Do not save last activity results
        - Update status (pre/post - phase2)
        - Launch activity on task stack
    5) No more activity on task stack:
        - Save last activity results
        - Update status (pre -> post OR end)
        - Call to exit view 'end_task'
    """
    participant = ParticipantProfile.objects.get(user=request.user.id)
    # Check if participant is doing the test for the first time:
    if 'cognitive_tests_status' not in participant.extra_json:
        init_participant_extra_json(participant)
    # task index is updated when the last task has been completed
    idx_task = participant.extra_json['cognitive_tests_current_task_idx']
    # Get current task context and name according to task idx:
    current_task_object = get_current_task_context(participant, idx_task)
    # 3 use cases: play / time for break / time to stop
    if current_task_object is not None and not participant.extra_json['cognitive_tests_break']:
        return launch_task(request, participant, current_task_object)
    elif current_task_object is not None:
        return exit_for_break(participant)
    else:
        return end_task(participant)


@login_required
@never_cache
def cognitive_task(request):
    """
        View used to render all activities in the pre/post assessment
        Render a base html file that uses a custom filter django tag to include the correct js scripts
    """
    participant = ParticipantProfile.objects.get(user=request.user.id)
    screen_params = Answer.objects.get(participant=participant, question__handle='prof-1').value
    current_task_idx = participant.extra_json["cognitive_tests_current_task_idx"]
    stack_tasks = participant.extra_json["cognitive_tests_task_stack"]
    current_task = f"{stack_tasks[current_task_idx]}"
    return render(request,
                  'pre-post-tasks/base_pre_post_app.html',
                  {"CONTEXT": {"screen_params": screen_params, "task": current_task}})


@login_required
def exit_view_cognitive_task(request):
    participant = ParticipantProfile.objects.get(user=request.user.id)
    idx_task = participant.extra_json['cognitive_tests_current_task_idx']
    # If the participant has just played, store results of last tasks:
    store_previous_task(request, participant, idx_task)
    # Update task index for next visit to the view
    update_task_index(participant)
    return redirect(reverse(cognitive_assessment_home))


def get_task_stack():
    """
        When user pass the test for the first time, the task stack is defined randomly here
    """
    all_tasks = CognitiveTask.objects.all().values('name')
    task_stack = [task['name'] for task in all_tasks]
    task_stack = ['workingmemory','taskswitch','enumeration', 'loadblindness', 'gonogo']
    # random.Random(0).shuffle(task_stack)
    return task_stack


def get_current_task_context(participant, idx_task):
    task_stack = participant.extra_json['cognitive_tests_task_stack']
    if idx_task < len(task_stack):
        if participant.extra_json['cognitive_tests_first_half']:
            participant.extra_json['cognitive_tests_break'] = idx_task == (NUMBER_OF_TASKS_PER_BATCH)
            participant.save()
        current_task_name = task_stack[idx_task]
        current_task_object = CognitiveTask.objects.values().get(name=current_task_name)
        return current_task_object
    else:
        participant.extra_json['cognitive_tests_current_task_idx'] = 0
        participant.extra_json['cognitive_tests_status'] = 'POST_TEST'
        participant.save()
        return None


def update_task_index(participant):
    """Objectives of this function are 2-folds:
        1) increment the current index of the cognitive_test that will be played
        2) Test if this index corresponds to the moment for a break
    """
    participant.extra_json['cognitive_tests_current_task_idx'] += 1
    participant.save()


def launch_task(request, participant, current_task_object):
    # No break + still tasks to play:
    # The task results will have to be stored right after coming back to this view
    participant.extra_json['task_to_store'] = True
    participant.save()
    screen_params = Answer.objects.get(participant=participant, question__handle='prof-1').value
    return render(request,
                  'pre-post-tasks/instructions/pre-post.html',
                  {'CONTEXT': {'participant': participant,
                               'current_task': current_task_object,
                               'screen_params': screen_params}})


def exit_for_break(participant):
    # A break but still tasks to play, i.e time to pass to second half of cognitive tests:
    # set participant extra json to same status (POST/PRE) with task index
    # When coming back after break, make sure the task to store is still set to False
    participant.extra_json['cognitive_tests_break'] = False
    participant.save()
    restart_participant_extra_json(participant,
                                   test_title=participant.extra_json['cognitive_tests_status'],
                                   task_index=NUMBER_OF_TASKS_PER_BATCH,
                                   is_first_half=False,
                                   task_to_store=False)
    return redirect(reverse('end_task'))


def end_task(participant):
    # Ok task is over let's close the task by rendering the usual end_task
    restart_participant_extra_json(participant,
                                   test_title='POST_TEST',
                                   task_index=0,
                                   is_first_half=True,
                                   task_to_store=False)
    return redirect(reverse('end_task'))


def store_previous_task(request, participant, idx_task):
    datas = request.POST.dict()
    if 'csrfmiddlewaretoken' in datas:
        del datas['csrfmiddlewaretoken']
    # We need to store the PREVIOUS task, decrement task idx:
    task_name = participant.extra_json['cognitive_tests_task_stack'][idx_task]
    task = CognitiveTask.objects.get(name=task_name)
    res = CognitiveResult()
    res.cognitive_task = task
    res.participant = participant
    res.idx = idx_task
    res.results = datas
    res.save()


def init_participant_extra_json(participant):
    participant.extra_json['cognitive_tests_task_stack'] = get_task_stack()
    restart_participant_extra_json(participant, test_title='PRE_TEST', task_index=0, task_to_store=False)


def restart_participant_extra_json(participant, test_title, task_index=0, is_first_half=True, task_to_store=True):
    participant.extra_json['cognitive_tests_status'] = test_title
    participant.extra_json['cognitive_tests_current_task_idx'] = task_index
    participant.extra_json['cognitive_tests_first_half'] = is_first_half
    participant.extra_json['task_to_store'] = task_to_store
    participant.save()


@login_required
def tutorial(request, task_name):
    participant = ParticipantProfile.objects.get(user=request.user.id)
    screen_params = Answer.objects.get(participant=participant, question__handle='prof-1').value
    return render(request, f"pre-post-tasks/instructions/includes/tutorials_{task_name}.html",
                  {"CONTEXT": {"screen_params": screen_params}})



from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages as django_messages
from django.views.decorators.cache import never_cache
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.translation import gettext_lazy as _

import json, datetime

from .models import ParticipantProfile, Study, ExperimentSession
from .forms import SignInForm, SignUpForm


def login_page(request, study=''):
    # If study key exists in request.session dict, get its values. This works when user requests the login page without specifying study extension and when the user already has a session
    if 'study' in request.session:
        study = request.session.get('study')
    # If user requests login page with a specific study extension, e.g. http://web-address.fr/study=name_of_study, the name_of_study will be assigned to the study variable
    # This also overwrites study name currently stored in user's session
    if 'study' in request.GET.dict():
        study = request.GET.dict().get('study')
    # Validate study name by checking with the database
    valid_study_title = bool(Study.objects.filter(name=study).count())
    if valid_study_title:
        # Normally, a participant has link to only one study. Thus, this should only be performed once
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
    # Plutôt utiliser un code erreur
    return render(request, 'login_page.html', {'CONTEXT': {
        'study': valid_study_title,
        'error': error,
        'form': form_sign_in
    }})


def signup_page(request):
    # Get study name from session
    study = Study.objects.get(name=request.session['study'])
    # Create form, validate, and save user credentials and (implicitly) create a ParticipantProfile object
    sign_up_form = SignUpForm(request.POST or None)
    if sign_up_form.is_valid():
        user = sign_up_form.save(study=study, commit=False)
        # user # Use set_password in order to hash password
        # user.save()
        login(request, user)
        return redirect(reverse(home))
    return render(request, 'signup_page.html', {'CONTEXT': {'form_user': sign_up_form}})


@login_required
@never_cache
def home(request):
    participant = request.user.participantprofile
    try:
        participant.set_current_session()
    except AssertionError:
        return redirect(reverse(thanks_page))

    if not participant.current_session_valid:
        return redirect(reverse(off_session_page))

    if not participant.current_task.prompt:
        return redirect(reverse(start_task))

    if participant.current_session:
         request.session['active_session'] = json.dumps(True)

    if 'messages' in request.session:
        for tag, content in request.session['messages'].items():
            print(tag, content)
            django_messages.add_message(request, getattr(django_messages, tag.upper()), content)
    return render(request, 'home_page.html', {'CONTEXT': {'participant': participant}})


@login_required
def start_task(request):
    if 'messages' in request.session:
        del request.session['messages']
    return redirect(reverse(request.user.participantprofile.current_task.view_name))


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
def end_session(request):
    participant = request.user.participantprofile
    participant.close_current_session()
    request.session['active_session'] = json.dumps(False)
    participant.queue_reminder()
    return redirect(reverse(thanks_page))


@login_required
def thanks_page(request):
    participant = request.user.participantprofile
    if participant.sessions.count():
        heading = 'La session est terminée'
        session_day = participant.sessions.first().day
        if session_day:
            next_date = participant.date.date() + datetime.timedelta(days=session_day-1)
            if datetime.date.today() == next_date:
                text = _('Votre entraînement n\'est pas fini pour aujourd\'hui, il vous reste une ' \
                       'session à effectuer durant la journée! Si vous voulez continuer immédiatement c\'est possible:'\
                       ' Déconnectez vous, reconnectez vous et recommencez !')
            else:
                text = _('Nous vous attendons la prochaine fois. Votre prochaine session est le {}'.format(next_date.strftime('%d/%m/%Y')))
        else:
            text = _('Nous vous attendons la prochaine fois.')
    else:
        heading = _('L\'étude est terminée')
        text = _('Merci, pour votre contribution à la science !')
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
def end_task(request):
    ''' A task exit_view function must change the 'exit_view_done' field of the request.session dict to True,
    in order to be run just once. The exit_view must also redirect back to this view. '''

    participant = request.user.participantprofile
    if participant.current_task.exit_view and not request.session.setdefault('exit_view_done', False):
        print('Redirecting to exit view: {}'.format(participant.current_task.exit_view))
        return redirect(reverse(participant.current_task.exit_view))
    if 'exit_view_done' in request.session:
        del request.session['exit_view_done']
    participant.pop_task()
    # Check if current session is empty
    if participant.current_session and not participant.current_task:
        return redirect(reverse(end_session))
    return redirect(reverse(home))


@login_required
def super_home(request):
    if request.user.is_authenticated & request.user.is_superuser:
        return render(request, 'super_home_page.html')

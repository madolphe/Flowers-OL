from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages as django_messages
from django.views.decorators.cache import never_cache
from django.utils import timezone
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
        user = authenticate(request, username=username, password=password)  # Check if data are valid
        if user:  # if user exists
            login(request, user)  # connect user
            destination = home_super if user.is_superuser else home
            return redirect(reverse(destination))
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
        login(request, user)
        return redirect(reverse(home))
    return render(request, 'signup_page.html', {'CONTEXT': {'form_user': sign_up_form}})


@login_required
@never_cache
def home(request):
    # Get the related ParticipantProfile instance
    participant = request.user.participantprofile

    # If current session cannot be assigned (i.e. session stack is empty), redirect to thanks page
    if not participant.set_current_session():
        return redirect(reverse(thanks_page))

    # I user tries to start session at a wrong time, redirect user to an appropriate page
    ref = participant.ref_timestamp
    if participant.current_session.in_future(ref):
        return redirect(reverse(off_session_page))  # too early
    elif participant.current_session.in_past(ref):
        if participant.current_session.required:
            return redirect(reverse(thanks_page))  # too late => can't proceed
        else:
            return redirect(reverse(end_session))  # too late => try next session

    # If current task has no prompt or actions, start task immediately
    if participant.current_task.unprompted:
        return redirect(reverse(start_task))

    # If participant has a session assigned, set request.session.active_session to True
    if participant.current_session:
         request.session['active_session'] = json.dumps(True)

    # If there are any messages, add them to django messages see https://docs.djangoproject.com/en/dev/ref/contrib/messages/
    if 'messages' in request.session:
        for tag, content in request.session['messages'].items():
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

    # Get next session if session stack is not empty, otherwise assign None to session
    session = None  # assigning None might be redundant, which is a good thing here!
    if participant.session_stack_peek():
        session = ExperimentSession.objects.get(pk=participant.session_stack_peek())

    if session:
        valid_period = session.get_valid_period(participant.ref_timestamp, string_format='%d %b %Y (%H:%M:%S)')
        start_info = f' opens on {valid_period[0]}' if valid_period[0] else ' opens whenever'
        deadline_info = f' and closes on {valid_period[1]}' if valid_period[1] else ' and remains open until you complete it'
        next_session_info = start_info + deadline_info
        return render(request, 'off_session_page.html', {'CONTEXT': {
            'next_session_info': _(next_session_info)}})


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
    if participant.session_stack_csv:
        heading = _('La session est terminée')
        next_session_pk = participant.session_stack_peek()
        if next_session_pk:
            next_session = participant.sessions.get(pk=next_session_pk)
            if not next_session.wait:
                text = _('Votre entraînement n\'est pas fini pour aujourd\'hui, il vous reste une ' \
                       'session à effectuer durant la journée! Si vous voulez continuer immédiatement c\'est possible:'\
                       ' Déconnectez vous, reconnectez vous et recommencez !')
            else:
                next_date = next_session.get_valid_period(participant.ref_timestamp, string_format='%d/%M/%Y')[0]
                text = _(f'Nous vous attendons la prochaine fois. Votre prochaine session est le {next_date}')
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
    # Check if participant has no more task in current session
    if participant.current_session and not participant.current_task:
        return redirect(reverse(end_session))
    return redirect(reverse(home))


from django.utils import timezone
@user_passes_test(lambda u: u.is_superuser)
def home_super(request):
    if request.user.is_authenticated:
        #* Create a participant for user if it does not exist
        #* ==========================
        s = Study.objects.get(name='demo')
        try:
            p = request.user.participantprofile
        except Exception:
            p = ParticipantProfile()
            p.user = request.user
            p.study = s
            p.save()
            p.populate_session_stack()
        #* Do regular home_view stuff
        #* ==========================
        try:
            p.set_current_session()
        except AssertionError:
            return redirect(reverse(thanks_page))

        time_stamp = p.last_session_timestamp.strftime('%d %b %Y (%H:%M:%S)') if p.last_session_timestamp else None
        valid_period = p.current_session.get_valid_period(p.ref_timestamp, string_format='%d %b %Y (%H:%M:%S)')

        now = timezone.now().strftime('%d %b %Y (%H:%M:%S)')
        now_is, destination = f'good time [{now}]', 'start_task'
        if p.current_session.in_future(p.ref_timestamp):
            now_is, destination = f'too early [{now}]', 'off_session_page'
        elif p.current_session.in_past(p.ref_timestamp):
            now_is = f'too late [{now}]'
            if p.current_session.required:
                destination = 'thanks_page'
            else:
                destination = 'end_session'
        
        return render(request, 'home_super.html', 
            {
                'CONTEXT': {
                    'p': p,
                    'time_stamp': time_stamp,
                    'valid_period': valid_period,
                    'now_is': now_is,
                    'destination': destination
                }
            }
        )


@user_passes_test(lambda u: u.is_superuser)
def reset_user_participant(request):
    s = Study.objects.get(name='demo')
    request.user.participantprofile.delete()
    request.user.participantprofile = None
    request.user.save()
    return redirect(reverse('home_super'))
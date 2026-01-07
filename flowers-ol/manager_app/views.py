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
from django.utils.module_loading import import_string
from django.http import Http404, HttpResponseNotAllowed

import json, datetime

from .utils import is_admin_team, _get_user_study
from .models import ParticipantProfile, Study, ExperimentSession, AdminPannel
from .forms import SignInForm, SignUpForm, ChangeUserPasswordForm


def login_page(request, study=''):
    # If study key exists in request.session dict, get its values. This works when user requests the login page without
    # specifying study extension and when the user already has a session
    if 'study' in request.session:
        study = request.session.get('study')
    # If user requests login page with a specific study extension, e.g. http://web-address.fr/study=name_of_study,
    # the name_of_study will be assigned to the study variable
    # This also overwrites study name currently stored in user's session
    if 'study' in request.GET.dict():
        study = request.GET.dict().get('study')
    # Validate study name by checking with the database
    valid_study_title = bool(Study.objects.filter(name=study).count())
    if valid_study_title:
        # Normally, a participant has link to only one study. Thus, this should only be performed once
        request.session['study'] = study  # store 'study' extension only once per session
    error = False
    form_sign_in = SignInForm(request.POST or None)
    if form_sign_in.is_valid():
        username = form_sign_in.cleaned_data['username']
        password = form_sign_in.cleaned_data['password']
        user = authenticate(request, username=username, password=password)  # Check if data are valid
        if user:
            login(request, user)
            if is_admin_team(user):
                return redirect(reverse(admin_home))
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
        login(request, user)
        return redirect(reverse(home))
    return render(request, 'signup_page.html', {'CONTEXT': {'form_user': sign_up_form}})


@login_required
@never_cache
def home(request):
    # Get the related ParticipantProfile instance
    participant = request.user.participantprofile

    # If current session cannot be assigned (i.e. session stack is empty), redirect to thanks page
    if not participant.set_current_session() or participant.excluded:
        return redirect(reverse(thanks_page))

    # I user tries to start session at a wrong time, redirect user to an appropriate page
    ref = participant.ref_timestamp
    if participant.current_session.in_future(ref):
        return redirect(reverse(off_session_page, kwargs={'case': 'early'}))  # too early
    elif participant.current_session.in_past(ref):
        if participant.current_session.required:
            return redirect(reverse(off_session_page, kwargs={'case': 'late'}))  # too late => can't proceed
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
def off_session_page(request, case):
    participant = request.user.participantprofile

    # Get next session if session stack is not empty, otherwise assign None to session
    session = None  # assigning None might be redundant, which is a good thing here!
    if participant.session_stack_peek():
        if case == 'early':
            reason = _(
                'La session ne peut pas être lancée parce qu\'il ne s\'est pas écoulé suffisamment de temps depuis votre dernière session.')
            instructions = _('Dans ce cas, revenez plus tard. Votre prochaine session')
            details = participant.get_next_session_info()
        elif case == 'late':
            reason = _(
                'Vous avez manqué une des sessions prévues. Si vous avez commencé une session plus tôt mais que vous ne l\'avez pas terminée à la date limite, la session est considérée comme manquée.')
            instructions = _(
                'Dans ce cas, vous n\'avez pas respecté le programme et vous ne pouvez pas poursuivre l\'expérience. Merci de participer à notre recherche.')
            details = None
        return render(request, 'off_session_page.html', {'CONTEXT': {
            'reason': reason, 'instructions': instructions, 'details': details}})
    else:
        return redirect(reverse('thanks_page'))


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
    next_date, next_session_info = None, None
    if participant.session_stack_csv:
        # If participant has sessions left
        heading = _('La session est terminée')
        next_session_pk = participant.session_stack_peek()
        if next_session_pk:
            if not participant.sessions.get(pk=next_session_pk).wait:
                # If session can start immediately
                text = _('Votre entraînement n\'est pas fini pour aujourd\'hui, il vous reste une ' \
                         'session à effectuer durant la journée! Si vous voulez continuer immédiatement c\'est possible:' \
                         ' Déconnectez vous, reconnectez vous et recommencez !')
            else:
                # If session has wait time
                next_session_info = participant.get_next_session_info()
                text = _('Nous vous attendons la prochaine fois. Votre prochaine session est le')
        else:
            text = _('Nous vous attendons la prochaine fois.')
        if participant.excluded:
            text = _(
                'Votre participation a été interrompue. Vous pouvez nous contacter pour plus d\'informations. Merci pour votre temps !')
    else:
        # If participant has no sessions left
        heading = _('L\'étude est terminée')
        text = _('Merci, pour votre contribution à la science !')
    return render(request, 'thanks_page.html', {'CONTEXT': {
        'heading': heading, 'text': text, 'next_session_info': next_session_info}})


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
        return redirect(reverse(participant.current_task.exit_view))
    if 'exit_view_done' in request.session:
        del request.session['exit_view_done']
    participant.pop_task()
    # Check if participant has no more task in current session
    if participant.current_session and not participant.current_task:
        return redirect(reverse(end_session))
    return redirect(reverse(home))


# All views below are for admin management pages
def admin_login_page(request):
    error = False
    form_sign_in = SignInForm(request.POST or None)

    if form_sign_in.is_valid():
        username = form_sign_in.cleaned_data['username']
        password = form_sign_in.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        # User doesn't exist
        if user is None:
            error = True
        # User authenticated but not superuser
        elif not is_admin_team(user):
            error = True
        # Superuser
        else:
            login(request, user)
            return redirect(reverse(admin_home))
    return render(request, 'admin_login_page.html', {
            'error': error,
            'form': form_sign_in
        })

def _resolve_panel_view(panel_view: str):
    """
    Allows two formats:
    - dotted path: 'manager_app.views.some_view'
    - url_name: 'some_url_name' (resolved via URLConf)
    """
    if "." in panel_view:
        return import_string(panel_view)

    match = resolve(reverse(panel_view))
    return match.func

@user_passes_test(lambda u: u.is_authenticated and is_admin_team(u), login_url="admin_login")
def admin_home(request, pannel_name=None):
    """
    - If pannel_name is None:
        load the 'home_pannel' for the user's Study
        and display a carousel (list) of panels for that Study.
    - Otherwise:
        load the requested panel (same Study) and:
          - if panel.view: call the view
          - otherwise: render the panel.html_page template
        + provide panel.css_page to the template
    """
    study = _get_user_study(request.user)

    if pannel_name is None:
        panel = AdminPannel.objects.filter(
            study=study,
            is_home=True
        ).first()
        if panel is None:
            raise Http404("Admin home panel 'home_pannel' introuvable pour cette Study.")
        panels = (
            AdminPannel.objects
            .filter(study=study, is_home=False)
            .order_by("name")
        )
        return render(request, "admin_home_pannel.html", {
            "panel": panel,
            "panels": panels,
            "panel_css": panel.css_page,
        })
    panel = AdminPannel.objects.filter(study=study, name=pannel_name).first()
    if panel is None:
        raise Http404(f"Admin panel '{pannel_name}' introuvable pour cette Study.")
    # 1) Dispatch to a view if defined
    if panel.view:
        view_func = _resolve_panel_view(panel.view)
        return view_func(request)
    # 2) Otherwise render template
    if panel.html_page:
        return render(request, panel.html_page, {
            "panel": panel,
            "panel_css": panel.css_page,
        })
    # Should not happen if data integrity is ensured
    raise Http404("Panel mal configuré (ni view ni html_page).")

@user_passes_test(lambda u: is_admin_team(u))
def admin_myprofile(request, study_name: str = "jold_ll"):
    """
    Page profil admin: GET.
    Assure qu'un participant existe, puis rend le template.
    """
    participant = _ensure_participant(request.user)
    debug = False
    if hasattr(participant, "extra_json") and isinstance(participant.extra_json, dict):
        debug = bool(participant.extra_json.get("debug_mode", False))
    task_stack = participant.task_stack_csv or ""
    try:
        time_stamp = participant.last_session_timestamp.strftime('%d %b %Y (%H:%M:%S)') if participant.last_session_timestamp else None
        valid_period = participant.current_session.get_valid_period(participant.ref_timestamp, string_format='%d %b %Y (%H:%M:%S)')
    except AttributeError:
        time_stamp = None
        valid_period = "Pas de session en cours, reset nécessaire"

    return render(request, "admin_pannels/myprofile.html", {
        "participant": participant,
        "debug": debug,
        "time_stamp": time_stamp,
        "valid_period": valid_period,
        "task_stack": task_stack,
    })

@user_passes_test(lambda u: is_admin_team(u))
def reset_user_participant(request):
    """
    Action destructive: POST-only.
    Supprime le ParticipantProfile existant puis en recrée un proprement.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    user = request.user
    study = _get_user_study(user)
    # Supprime l'existant si présent
    participant = getattr(user, "participantprofile", None)
    if participant is not None:
        participant.delete()
        # invalider le cache de relation
        if hasattr(user, "_state") and hasattr(user._state, "fields_cache"):
            user._state.fields_cache.pop("participantprofile", None)
    # Recrée un participant propre
    _ensure_participant(user, study=study)
    django_messages.success(request, "Participant remis à zéro.")
    return redirect('admin_myprofile')

def _ensure_participant(user, study: Study=None) -> ParticipantProfile:
    """
    Garantit qu'un ParticipantProfile existe pour l'utilisateur et la Study donnée.
    Ne fait AUCUN render/redirect: utilitaire pur.
    """
    participant = getattr(user, "participantprofile", None)
    if participant is None:
        if study is None:
            raise ValueError("Study doit être fournie si le ParticipantProfile n'existe pas.")
        participant = ParticipantProfile(user=user, study=study)
        participant.save()
        participant.populate_session_stack()
        _ = participant.set_current_session()

    return participant

@user_passes_test(lambda u: is_admin_team(u))
def switch_participant(request):
    participant = request.user.participantprofile
    if request.method == "POST":
        if hasattr(participant, 'extra_json'):
            debug_value = request.POST.get('debug') == 'on'
            participant.extra_json['debug_mode'] = debug_value
            participant.save()
            django_messages.success(request, 'Mode debug mis à jour.')
        else:
            django_messages.error(request, 'Participant has no extra_json field.')
    return redirect('admin_myprofile')

@user_passes_test(lambda u: is_admin_team(u), login_url="admin_login")
def admin_change_user_password(request):
    form = ChangeUserPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        new_password = form.cleaned_data["new_password"]
        try:
            user = User.objects.get(username=username)
            if user.participantprofile.study != _get_user_study(request.user):
                raise PermissionError(
                    "Vous ne pouvez pas modifier le mot de passe d’un utilisateur d'une autre étude."
                )
            if is_admin_team(user) and user != request.user:
                raise PermissionError(
                        "Vous ne pouvez pas modifier le mot de passe d’un autre administrateur."
                    )
            user.set_password(new_password)
            user.save()
            django_messages.success(
                request,
                f"Le mot de passe de l’utilisateur « {username} » a été modifié."
            )
        except User.DoesNotExist:
            django_messages.error(
                request,
                f"Impossible de modifier le mot de passe : l’utilisateur « {username} » n’existe pas."
            )
        except PermissionError as e:
            django_messages.error(request, str(e))
        return redirect("admin_change_user_password")
    return render(request, "admin_pannels/change_usr_password.html", {
        "form": form,
    })


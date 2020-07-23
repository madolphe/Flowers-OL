from datetime import date, timedelta, datetime
from django.contrib import messages
from background_task import background
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.utils import timezone
from . import models


def add_message(request, message, tag='info'):
    request.session.setdefault('messages', {})[tag] = message


@background(schedule=0)
def send_delayed_email(to, sender, subject, message_template):
    print('Sending email to {}'.format(to))
    send_mail(
        subject = subject,
        html_message = message_template,
        message = strip_tags(message_template),
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [to],
        fail_silently = False
    )


@background(schedule=0)
def send_delayed_email_2():
    print('Sending email test')
    send_mail(
        subject = 'Testing process tasks',
        message = 'This is a test',
        from_email = 'noreply-flowers@inria.fr',
        recipient_list = ['alexandr.ten@inria.fr', 'maxime.adolphe@inria.fr'],
        fail_silently = False
    )


def assign_mot_condition(participant):
    # First, check if participant study is zpdes_admin
    if participant.study.name == 'zpdes_admin':
        participant.extra_json['condition'] = 'baseline'
        print("Condition saved:", participant.extra_json['condition'])
        zpdes_group_nb = len(models.ParticipantProfile.objects.filter(extra_json__contains='zpdes'))
        baseline_group_nb = len(models.ParticipantProfile.objects.filter(extra_json__contains='baseline'))
        print("Number in zpdes/baseline: ({}/{})".format(zpdes_group_nb, baseline_group_nb))
        participant.save()
    else:
        # First check if the participant has attentional problems:
        attention_responses = models.Answer.objects.filter(participant=participant)
        score = 0
        key = 0
        for resp in attention_responses:
            if resp.question.instrument == "get_attention":
                if key <= 3 and int(resp.value) > 2:
                    score += 1
                elif int(resp.value) > 3:
                    score += 1
                key += 1
        # If score is to high, turn extra_json['attention_pb'] to true:
        participant.extra_json['attention_pb'] = (score >= 4)
        # Then assign a condition depending on the cardinal of the population:
        zpdes_group_nb = len(models.ParticipantProfile.objects.filter(extra_json__contains='zpdes'))
        baseline_group_nb = len(models.ParticipantProfile.objects.filter(extra_json__contains='baseline'))
        print("Number in zpdes/baseline: ({}/{})".format(zpdes_group_nb, baseline_group_nb))
        # Assign user in the smallest group
        if zpdes_group_nb > baseline_group_nb:
            participant.extra_json['condition'] = 'baseline'
        else:
            participant.extra_json['condition'] = 'zpdes'
        print("Condition saved:", participant.extra_json['condition'])
        zpdes_group_nb = len(models.ParticipantProfile.objects.filter(extra_json__contains='zpdes'))
        baseline_group_nb = len(models.ParticipantProfile.objects.filter(extra_json__contains='baseline'))
        print("Number in zpdes/baseline: ({}/{})".format(zpdes_group_nb, baseline_group_nb))
        participant.save()

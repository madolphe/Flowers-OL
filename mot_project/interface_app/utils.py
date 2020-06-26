import random, warnings
from .models import ParticipantProfile
from datetime import date, timedelta
from django.contrib import messages


def assign_condition(participant, save=False):
    if participant.study.name == 'jold_ll':
        participant.wind = random.sample([0,2,4], 1)[0]
        participant.plat = random.sample([-1,0,1], 1)[0]
        participant.dist = random.randint(0,1)
    elif participant.study.name == 'jold_mot':
        warnings.warn('no fixed user condition for JOLD_MOT study, no condition assigned')
    elif participant.study.name == 'zpdes_mot':
        warnings.warn('no fixed user condition for ZPDES_MOT study, no condition assigned')
    else:
        warnings.warn('Study name unidentified, no condition assigned')
    if save: participant.save()

def add_message(request, message, tag='info'):
    request.session.setdefault('messages', {})[tag] = message

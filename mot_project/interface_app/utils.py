import random, warnings
from .models import ParticipantProfile, Answer


def assign_condition(participant):
    if participant.study.name == 'jold_ll':
        participant.wind = random.sample([0,2,4], 1)[0]
        participant.plat = random.sample([-1,0,1], 1)[0]
        participant.dist = random.randint(0,1)
    elif participant.study.name == 'jold_mot':
        warnings.warn('no fixed user condition for JOLD_MOT study, no condition assigned')

    elif participant.study.name == 'zpdes_mot':
        # First check if the participant has attentional problems:
        attention_responses = Answer.objects.filter(participant=participant)
        score = 0
        for key, resp in enumerate(attention_responses.values()):
            if resp.question.instrument == "get_attention":
                if key <= 3 and resp['answer'] > 2:
                    score += 1
                elif resp['answer'] > 3:
                    score += 1
            print(score)
        # If score is to high, turn extra_json['attention_pb'] to true:
        participant.extra_json['attention_pb'] = (score >= 4)
        # Then assign a condition depending on the cardinal of the population:
        zpdes_group_nb = len(ParticipantProfile.objects.filter(extra_json__has_key='zpdes'))
        baseline_group_nb = len(ParticipantProfile.objects.filter(extra_json__has_key='baseline'))
        print("Number in zpdes/baseline: ({}/{})".format(zpdes_group_nb, baseline_group_nb))
        # Assign user in the smallest group
        if zpdes_group_nb > baseline_group_nb:
            participant.extra_json['condition'] = 'baseline'
        else:
            participant.extra_json['condition'] = 'zpdes'
        print("Condition saved:",  participant.extra_json['condition'])
        participant.save()
    elif participant.study.name == 'zpdes_admin':
        # For admin study, zpdes is the only algorithm tested:
        participant.extra_json['condition'] = 'zpdes'
    else:
        warnings.warn('study string unidentified, no condition assigned')


def add_message(request, message, tag='info'):
    request.session.setdefault('messages', {})[tag] = message


def assign_mot_condition(participant):
    # First check if the participant has attentional problems:
    attention_responses = Answer.objects.filter(participant=participant)
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
    zpdes_group_nb = len(ParticipantProfile.objects.filter(extra_json__contains='zpdes'))
    baseline_group_nb = len(ParticipantProfile.objects.filter(extra_json__contains='baseline'))
    print("Number in zpdes/baseline: ({}/{})".format(zpdes_group_nb, baseline_group_nb))
    # Assign user in the smallest group
    if zpdes_group_nb > baseline_group_nb:
        participant.extra_json['condition'] = 'baseline'
    else:
        participant.extra_json['condition'] = 'zpdes'
    print("Condition saved:", participant.extra_json['condition'])
    zpdes_group_nb = len(ParticipantProfile.objects.filter(extra_json__contains='zpdes'))
    baseline_group_nb = len(ParticipantProfile.objects.filter(extra_json__contains='baseline'))
    print("Number in zpdes/baseline: ({}/{})".format(zpdes_group_nb, baseline_group_nb))
    participant.save()

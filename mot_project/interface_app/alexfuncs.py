import random, warnings
from .models import ParticipantProfile, Responses


def assign_condition(user, study):
    if study == 'jold_ll':
        pt_ll = ParticipantProfile.objects.get(user=user.id)
        pt_ll.wind = random.sample([0, 2, 4], 1)[0]
        pt_ll.plat = random.sample([-1, 0, 1], 1)[0]
        pt_ll.dist = random.randint(0, 1)
        pt_ll.user = user
        pt_ll.save()
    elif study == 'jold_mot':
        warnings.warn('no fixed user condition for JOLD_MOT study, no condition assigned')
    elif study == 'zpdes-mot':
        participant = ParticipantProfile.objects.get(user=user.id)
        # First, check attention results
        attention_responses = Responses.objects.filter(participant=participant)
        score = 0
        for key, resp in enumerate(attention_responses.values()):
            print("In loop", key)
            print(key, resp, key)
            if key <= 3 and resp['answer'] > 2:
                    score += 1
            elif resp['answer'] > 3:
                    score += 1
        print(score)
        # If score is to high, assign condition 'attention_pb'
        if score >= 4:
            participant.condition = 'attention_pb'
            participant.save()
        # Else, check numbers of participants in each condition
        else:
            zpdes_group_nb = len(ParticipantProfile.objects.filter(condition='zpdes'))
            baseline_group_nb = len(ParticipantProfile.objects.filter(condition='baseline'))
            print("Number in zpdes/baseline: ({}/{})".format(zpdes_group_nb, baseline_group_nb))
            # Assign user in the smallest group
            if zpdes_group_nb > baseline_group_nb:
                participant.condition = 'baseline'
            else:
                participant.condition = 'zpdes'
            participant.save()
        print("Condition saved:", participant.condition)
    else:
        warnings.warn('study string unidentified, no condition assigned')

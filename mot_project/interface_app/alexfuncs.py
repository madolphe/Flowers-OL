import random, warnings
from .models import ParticipantProfile

def assign_condition(user, study):
    print(user, study)
    if study=='jold_ll':
        pt_ll = ParticipantProfile.objects.get(user=user.id)
        pt_ll.wind = random.sample([0,2,4], 1)[0]
        pt_ll.plat = random.sample([-1,0,1], 1)[0]
        pt_ll.dist = random.randint(0,1)
        pt_ll.user = user
        pt_ll.save()
    elif study=='jold_mot':
        warnings.warn('no fixed user condition for JOLD_MOT study, no condition assigned')
    elif study=='zpdes_mot':
        warnings.warn('no fixed user condition for ZPDES_MOT study, no condition assigned')
    else:
        warnings.warn('study string unidentified, no condition assigned')

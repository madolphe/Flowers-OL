import random, warnings
from .models import JOLD_params_LL

def assign_condition(user, study):
    print(user, study)
    if study=='jold_ll':
        ll_params = JOLD_params_LL()
        ll_params.wind = random.sample([0,2,4], 1)[0]
        ll_params.plat = random.sample([-1,0,1], 1)[0]
        ll_params.dist = random.randint(0,1)
        ll_params.participant = user
        ll_params.save()
    elif study=='jold_mot':
        warnings.warn('no fixed user condition for JOLD_MOT study, no condition assigned')
    elif study=='zpdes_mot':
        warnings.warn('no fixed user condition for ZPDES_MOT study, no condition assigned')
    else:
        warnings.warn('study string unidentified, no condition assigned')

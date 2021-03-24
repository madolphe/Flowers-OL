from survey_app import models


def assign_mot_condition(participant):
    # First, check if participant study is zpdes_admin
    if participant.study.name == 'zpdes_admin':
        participant.extra_json['condition'] = 'zpdes'
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
        # print("Condition saved:", participant.extra_json['condition'])
        zpdes_group_nb = len(models.ParticipantProfile.objects.filter(extra_json__contains='zpdes'))
        baseline_group_nb = len(models.ParticipantProfile.objects.filter(extra_json__contains='baseline'))
        print("Number in zpdes/baseline: ({}/{})".format(zpdes_group_nb, baseline_group_nb))
        participant.save()
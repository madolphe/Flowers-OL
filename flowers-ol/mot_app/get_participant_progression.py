from datetime import datetime
import pytz

from .models import Episode, CognitiveResult
from manager_app.models import ParticipantProfile

from statistics import mean, stdev


def get_mean_idle_time(participant):
    all_episodes = Episode.objects.all().filter(participant__username=participant)
    sessions = {}
    for episode in all_episodes:
        if episode.id_session not in sessions:
            sessions[episode.id_session] = []
        sessions[episode.id_session].append(episode)
    check_episode_date()
    idle_times = {}
    for session_key, session_content in sessions.items():
        shift_session = session_content[1::]
        idle_times[session_key] = []
        for episode, next_episode in zip(session_content, shift_session):
            if next_episode:
                delta = next_episode.date - episode.date
                episode_length = episode.tracking_time + episode.presentation_time + episode.fixation_time + episode.probe_time
                idle_times[session_key].append((delta.total_seconds() - episode_length))
        print(sum(idle_times[session_key]) / len(idle_times[session_key]))


def check_episode_date():
    pass


def get_exp_status(study):
    all_participants = ParticipantProfile.objects.all().filter(study__name=study)
    nb_participants = len(all_participants)
    nb_cog_assessment_list = [(participant, get_nb_cog_assessment_for_participant(participant)) for participant in
                              all_participants]
    nb_participants_in = sum([nb == 8 for (participant, nb) in nb_cog_assessment_list])
    zpdes_participants, baseline_participants, none_participants = get_groups(all_participants)
    nb_baseline, nb_zpdes = len(baseline_participants), len(zpdes_participants)
    descriptive_dict = {'zpdes': get_progression(zpdes_participants),
                        'baseline': get_progression(baseline_participants),
                        'cog': get_progression(none_participants)}
    return nb_participants, nb_participants_in, nb_baseline, nb_zpdes, descriptive_dict


def get_nb_cog_assessment_for_participant(participant):
    particpants_cog_results = CognitiveResult.objects.all().filter(participant=participant)
    return len(particpants_cog_results)


def get_groups(all_participants):
    zpdes_participants, baseline_participants, none_participants = [], [], []
    for participant in all_participants:
        if "condition" in participant.extra_json:
            if participant.extra_json["condition"] == "zpdes":
                zpdes_participants.append(participant)
            else:
                baseline_participants.append(participant)
        else:
            none_participants.append(participant)
    return zpdes_participants, baseline_participants, none_participants


def get_progression(participants_list):
    descriptive_dict = {}
    for participant in participants_list:
        pk = participant.session_stack_peek()
        if not pk:
            participant_progression = [1 for i in range(10)]
        else:
            next_session = participant.sessions.get(pk=pk)
            participant_progression = [1 for i in range(next_session.index)]
            if bool(participant.current_session):
                if len(participant_progression) == 0:
                    participant.last_session_timestamp = participant.origin_timestamp
                # participant has connected but didnt finished session of the day
                if (get_time_since_last_session(participant) - 1) < 3:
                    participant_progression.append(-1)
                else:
                    participant_progression.append(-2)
            else:
                # participant has not reconnected:
                s = participant.sessions.get(pk=participant.session_stack_peek())
                if s.in_future(participant.ref_timestamp):
                    participant_progression.append(0)
                else:
                    # session is available but has not started it yet --> -1 or -2
                    participant.current_session = s
                    if get_time_since_last_session(participant) < 3 + participant.current_session.wait['days']:
                        participant_progression.append(-1)
                    else:
                        participant_progression.append(-2)
        if 'condition' in participant.extra_json:
            cond = participant.extra_json['condition']
            nb_episode = get_number_episode_played(participant)
            idle_time = get_mean_idle_time(participant) / 1000
        else:
            cond = 'no_group'
            nb_episode = 0
            idle_time = 0
        none_blocks = [0 for i in range(10 - len(participant_progression))]
        descriptive_dict[participant.user.username] = (
            cond, participant_progression, none_blocks, nb_episode, idle_time)
    return descriptive_dict


def get_number_episode_played(participant):
    return len(Episode.objects.all().filter(participant=participant.user))


def get_mean_idle_time(participant):
    episodes = Episode.objects.all().filter(participant=participant.user)
    mean_idles = [episode.idle_time for episode in episodes]
    return sum(mean_idles) / len(mean_idles)


def get_time_since_last_session(participant):
    """
    Return -1 if available but not finished within 3 days
    Return -2 if available but not finished in more than 3 days
    """
    return (datetime.now(pytz.utc) - participant.last_session_timestamp).days


def get_staircase_episodes(study, parser):
    participants = ParticipantProfile.objects.all().filter(study__name=study)
    all_participants = {}
    for participant in participants:
        if 'condition' in participant.extra_json:
            if participant.extra_json['condition'] == 'baseline':
                episodes = Episode.objects.all().filter(participant=participant.user)
                average_dict, std_dict = get_staircase(participant, episodes, parser)
                all_participants[participant.user.username] = [average_dict, std_dict]
    return all_participants


def get_staircase(participant, episodes, parser):
    # main_list = [f'nb{i}' for i in range(2, 8)]
    current_dict = {}
    for episode in episodes:
        # activity = parser.parse_activity(episode)
        # main = activity['act']['MAIN'][0]
        # activity_lvl = activity['act']['MAIN'][0] + activity['act'][main_list[main]][0]
        # activity_lvl = activity['act']['MAIN'][0]
        if str(episode.date.date()) not in current_dict:
            current_dict[str(episode.date.date())] = []
        current_dict[str(episode.date.date())].append(episode.n_targets)
    average_dict, std_dict = {}, {}
    for date, values in current_dict.items():
        average_dict[date] = mean(values)
        std_dict[date] = stdev(values)
    return average_dict, std_dict


if __name__ == '__main__':
    # get_mean_idle_time("v1_ubx")
    nb_participants, nb_participants_in, descriptive_dict = get_exp_status("v1_ubx")
    print(nb_participants, nb_participants_in, descriptive_dict)

from datetime import datetime
import pytz

from .models import Episode, CognitiveResult
from manager_app.models import ParticipantProfile

from statistics import mean, stdev
import numpy as np


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
        if 'stop' in participant.extra_json:
            participant_progression = [-3 for i in range(10)]
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


def get_staircase_episodes(study):
    participants = ParticipantProfile.objects.all().filter(study__name=study)
    all_participants = {}
    for participant in participants:
        if 'condition' in participant.extra_json:
            if participant.extra_json['condition'] == 'baseline':
                episodes = Episode.objects.all().filter(participant=participant.user)
                average_lvl_dict, std_lvl_dict, mean_idle_time_dict = get_staircase_lvl(episodes)
                traj_dict = get_trajectory(episodes)
                if len(average_lvl_dict.keys()) > 1:
                    all_participants[participant.user.username] = [average_lvl_dict, std_lvl_dict, mean_idle_time_dict,
                                                                   traj_dict]
    return all_participants


def get_staircase_lvl(episodes):
    current_dict = sort_episodes_by_date(episodes)
    average_lvl_dict, std_lvl_dict, mean_idle_time_dict = {}, {}, {}
    for date, values in current_dict.items():
        average_lvl_dict[date] = mean([episode.n_targets for episode in values])
        std_lvl_dict[date] = stdev([episode.n_targets for episode in values])
        mean_idle_time_dict[date] = mean([episode.idle_time / 1000 for episode in values])
    return average_lvl_dict, std_lvl_dict, mean_idle_time_dict


def sort_episodes_by_date(episodes):
    dict = {}
    for episode in episodes:
        if str(episode.date.date()) not in dict:
            dict[str(episode.date.date())] = []
        dict[str(episode.date.date())].append(episode)
    return dict


def get_trajectory(episodes):
    final_dict = {'n_targets': [], 'speed': [], 'probe_duration': [], 'tracking_duration': [], 'radius': []}
    for episode in episodes:
        parsed_episode = parse_episode(episode)
        for key in parsed_episode.keys():
            final_dict[key].append(parsed_episode[key])
    return final_dict


def parse_episode(episode):
    # Just not to break everything:
    values_ref = {'n_targets': np.array([2, 3, 4, 5, 6, 7], dtype=float),
                  'speed': np.array([2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0], dtype=float),
                  'tracking_duration': np.array([3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0], dtype=float),
                  'probe_duration': np.array([12.0, 11.0, 10.0, 9.0, 8.0, 7.0, 6.0], dtype=float),
                  'radius': np.array([1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.6], dtype=float)}
    lvls_ref = ["nb2", "nb3", "nb4", "nb5", "nb6", "nb7"]
    episode_dict = {}
    episode_dict['speed'] = np.where(values_ref['speed'] == float(episode.speed_max))[0][0]
    episode_dict['n_targets'] = np.where(values_ref['n_targets'] == float(episode.n_targets))[0][0]
    episode_dict['tracking_duration'] = np.where(values_ref['tracking_duration'] == float(episode.tracking_time))[0][0]
    episode_dict['probe_duration'] = np.where(values_ref['probe_duration'] == float(episode.probe_time))[0][0]
    episode_dict['radius'] = np.where(values_ref['radius'] == float(episode.radius))[0][0]
    return episode_dict


if __name__ == '__main__':
    # get_mean_idle_time("v1_ubx")
    nb_participants, nb_participants_in, descriptive_dict = get_exp_status("v1_ubx")
    print(nb_participants, nb_participants_in, descriptive_dict)
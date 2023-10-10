import os
import django
import copy
import math

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import importlib
from datetime import datetime
import pytz
import numpy as np
from scipy import spatial
from pathlib import Path

from matplotlib.cm import ScalarMappable

import imageio

# Connection to flowers-DB:
flowers_ol = importlib.import_module("flowers-ol.settings")

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "flowers-ol.settings"
)
django.setup()
import kidlearn_lib as k_lib
from kidlearn_lib import functions as func

from mot_app.models import CognitiveResult, Episode
from manager_app.models import ParticipantProfile, Study
from survey_app.models import Answer
from mot_app.sequence_manager.seq_manager import MotParamsWrapper

NB_COG_TASKS = 18


# ######################################################################################################################
# Utils function to run temporary the code:
def get_exp_status(study, exclude_unfinished=True):
    all_participants = ParticipantProfile.objects.all().filter(study__name=study)
    nb_participants = len(all_participants)
    nb_cog_assessment_list = [(participant, get_nb_cog_assessment_for_participant(participant)) for participant in
                              all_participants]
    nb_participants_in = sum([nb == NB_COG_TASKS // 2 for (participant, nb) in nb_cog_assessment_list])
    if exclude_unfinished:
        for (participant, nb) in nb_cog_assessment_list:
            if nb != NB_COG_TASKS:
                all_participants.get(user_id=participant.user.id).delete()
    zpdes_participants, baseline_participants, none_participants = get_groups(all_participants)
    nb_baseline, nb_zpdes = len(baseline_participants), len(zpdes_participants)
    # descriptive_dict = {'zpdes': get_progression(zpdes_participants),
    #                     'baseline': get_progression(baseline_participants),
    #                     'cog': get_progression(none_participants)}
    descriptive_dict = {}
    return nb_participants, nb_participants_in, nb_baseline, nb_zpdes, descriptive_dict, zpdes_participants, \
        baseline_participants


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


def get_time_since_last_session(participant):
    """
    Return -1 if available but not finished within 3 days
    Return -2 if available but not finished in more than 3 days
    """
    return (datetime.now(pytz.utc) - participant.last_session_timestamp).days


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


def get_mean_idle_time(participant):
    episodes = Episode.objects.all().filter(participant=participant.user)
    mean_idles = [episode.idle_time for episode in episodes]
    return sum(mean_idles) / len(mean_idles)


def get_number_episode_played(participant):
    return len(Episode.objects.all().filter(participant=participant.user))


def sort_episodes_by_date(episodes):
    """Sort activities per session"""
    dict = {}
    last_key_played_date = episodes[0].date
    dict[str(episodes[0].date.date())] = []
    for episode in episodes:
        if str(episode.date.date()) not in dict:
            if (episode.date - last_key_played_date).total_seconds() / 60 < 60:
                episode.date = last_key_played_date
            else:
                dict[str(episode.date.date())] = []
                last_key_played_date = episode.date
        dict[str(episode.date.date())].append(episode)
    tmp_episode = []
    for session_date, list_episodes in dict.items():
        tmp_episode = []
        for episode in list_episodes:
            if len(tmp_episode) > 0:
                if episode.episode_number != tmp_episode[-1].episode_number:
                    tmp_episode.append(episode)
            else:
                tmp_episode.append(episode)
        dict[session_date] = copy.deepcopy(tmp_episode)
    # If within a day there is less than 5 episodes just delete the session
    key_to_pop = []
    for key in dict:
        if len(dict[key]) < 5:
            key_to_pop.append(key)
    for key in key_to_pop:
        dict.pop(key)
    return dict


def get_cumulative_episode(episodes):
    cumulative_episodes = {}
    len_cumulative_episodes = {}
    for participant, episodes_participant in episodes.items():
        print(participant)
        episodes_tmp = []
        cumulative_episodes[participant], len_cumulative_episodes[participant] = {}, {}
        for session_idx, session_episode in episodes_participant.items():
            episodes_tmp += session_episode
            cumulative_episodes[participant][session_idx] = copy.deepcopy(episodes_tmp)
            len_cumulative_episodes[participant][session_idx] = len(cumulative_episodes[participant])
    return cumulative_episodes, len_cumulative_episodes


def split_sessions_in_blocks(episodes, nb_episodes=30):
    return_dict = {}
    nb_dict = {}
    for session_key, session_values in episodes.items():
        nb_blocks = (len(session_values) // nb_episodes) + 1
        for block in range(nb_blocks):
            if len(session_values[block * nb_episodes:(block + 1) * (nb_episodes)]) >= (nb_episodes // 2):
                return_dict[f"{session_key}_{block}"] = session_values[block * nb_episodes:(block + 1) * (nb_episodes)]
                nb_dict[f"{session_key}_{block}"] = len(session_values[block * nb_episodes:(block + 1) * (nb_episodes)])
    return return_dict, nb_dict


# ######################################################################################################################
# Here we take care of ZPDES participants:
# First some processings regarding success rate, mean activity proposed and frequency of each main dim
# This some kind of position of ZPD through time
def get_true_episodes(participant_list, nb_episodes=20, keep_ntargets=None):
    """
    keep_ntargets: int , specification of a certain nb_target lvl to keep (i.e keep only episodes with n_targets = 2)
    """
    sort_episodes, sort_episodes_true, participants_nb_per_block, participants_nb_per_block_true = {}, {}, {}, {}
    for participant in participant_list:
        episodes = Episode.objects.all().filter(participant=participant.user)
        participant_sort_episodes = sort_episodes_by_date(episodes)
        if keep_ntargets:
            participant_sort_episodes = {k: list(filter(lambda episode: episode.n_targets == keep_ntargets, v)) for k, v
                                         in participant_sort_episodes.items()}
        # We split the sessions into blocks at this stage so that the get_true_episodes will be automaticaly split:
        participant_sort_episodes, participant_nb_per_block = split_sessions_in_blocks(participant_sort_episodes,
                                                                                       nb_episodes=nb_episodes)
        participant_sort_episodes_true = {k: list(filter(lambda episode: episode.get_results == 1, v)) for k, v in
                                          participant_sort_episodes.items()}
        nb_per_block_true = {k: len(episodes) for k, episodes in participant_sort_episodes_true.items()}
        sort_episodes[participant] = participant_sort_episodes
        sort_episodes_true[participant] = participant_sort_episodes_true
        participants_nb_per_block[participant] = participant_nb_per_block
        participants_nb_per_block_true[participant] = nb_per_block_true
    # sort_episodes = exclude_participant(sort_episodes, nb_episodes=nb_episodes)
    # sort_episodes_true = exclude_participant(sort_episodes_true, nb_episodes=nb_episodes)
    return sort_episodes, sort_episodes_true, participants_nb_per_block, participants_nb_per_block_true


def get_mean_success_ps(all_episodes, true_episodes):
    participants_success_ps = {}
    for participant, participant_sessions in all_episodes.items():
        particpant_mean_success = {}
        for session_id, episodes_list in participant_sessions.items():
            try:
                particpant_mean_success[session_id] = len(true_episodes[participant][session_id]) / len(episodes_list)
            except ZeroDivisionError:
                print('Cest biwzarre')
        participants_success_ps[participant] = particpant_mean_success
    return participants_success_ps


def get_frequency_of_ntargets(episodes):
    n_targets_range = [i for i in range(2, 8)]
    participants_frequency_ntargets = {}
    for participant, participant_sessions in episodes.items():
        participant_sessions_freq = {}
        for session_id, episodes in participant_sessions.items():
            tmp_session = [episode.n_targets for episode in episodes]
            tmp_freq = [tmp_session.count(ntarget_value) for ntarget_value in n_targets_range]
            tmp_freq = list(np.array(tmp_freq) / sum(tmp_freq))
            participant_sessions_freq[session_id] = tmp_freq
        participants_frequency_ntargets[participant] = participant_sessions_freq
    return participants_frequency_ntargets


def get_average_activity(episodes):
    """
    Returns dict {participant_key: {nb_target_key: {session_id: [mean per sub_dim]}}}
    """
    participants_average_episode = {}
    for participant, participant_sessions in episodes.items():
        tmp_sort_episode_nb_target = {k: {} for k in range(2, 8)}
        for session_id, episodes in participant_sessions.items():
            for episode in episodes:
                tmp_episode = [episode.speed_max, episode.tracking_time, episode.probe_time, episode.radius]
                if session_id not in tmp_sort_episode_nb_target[episode.n_targets]:
                    tmp_sort_episode_nb_target[episode.n_targets][session_id] = tmp_episode
                else:
                    # Compute the mean of new episode
                    tmp_sort_episode_nb_target[episode.n_targets][session_id] = list(0.5 * np.add(
                        tmp_sort_episode_nb_target[episode.n_targets][session_id], tmp_episode))
        participants_average_episode[participant] = tmp_sort_episode_nb_target
    return participants_average_episode


def get_accuracy_per_episode(episodes):
    participants_success_ps, participants_success_ps_std = {}, {}
    for participant, participant_sessions in episodes.items():
        particpant_mean_success, participant_std = {}, {}
        for session_id, episodes_list in participant_sessions.items():
            # acc_sess = [(episode.nb_target_retrieved + episode.nb_distract_retrieved) / 16 for episode in episodes_list]
            # acc_sess = [episode.nb_target_retrieved /episode.n_targets  for episode in episodes_list]
            # acc_sess = [1 - (episode.nb_distract_retrieved / episode.n_distractors) for episode in episodes_list]
            acc_sess = [extract_F1(episode) for episode in episodes_list]
            particpant_mean_success[session_id] = np.mean(acc_sess)
            participant_std[session_id] = np.std(acc_sess)
        participants_success_ps[participant] = particpant_mean_success
        participants_success_ps_std[participant] = participant_std
    return participants_success_ps, participants_success_ps_std


# ######################################################################################################################
# Then some graph about exploration
# 1) Iterate over participants:
def get_participants_hulls_per_session(episodes):
    """ Iter through all participants to retrieve the array of all hull per sessions"""
    hull_volume_per_participant = {}
    for participant, participant_sessions in episodes.items():
        hull_volume_per_participant[participant.user.username] = get_participant_hull_volume(participant_sessions)
    return hull_volume_per_participant


# 2) Iterate over sessions
def get_participant_hull_volume(participant_sessions):
    """
    For a given participant, for all sessions retrieve first the hull and then the volumes for each session
    """
    hulls_volume = {}
    for session_id, session_points in participant_sessions.items():
        if len(session_points) > 5:
            tmp_hull = get_hull_per_session(session_points)
            hulls_volume[session_id] = tmp_hull.volume
    return hulls_volume


# 3) Get hull per session
def get_hull_per_session(session_points):
    """Transform all points from a session to array of episodes and compute the hull of the session"""
    episode_array = list(
        map(lambda episode: [episode.n_targets, episode.speed_max, episode.tracking_time, episode.probe_time,
                             episode.radius],
            session_points))
    episode_array = np.array(episode_array)
    valid_dims = [np.any(episode_array[:, col] != episode_array[0, col]) for col in range(5)]
    if all(valid_dims):
        hull = spatial.ConvexHull(points=episode_array, qhull_options='QJ')
    else:
        index = []
        array_kept = []
        for valid_dim_index in range(len(valid_dims)):
            if not valid_dims[valid_dim_index]:
                index.append(episode_array[0, valid_dim_index])
            else:
                array_kept.append(episode_array[:, valid_dim_index])
        hull = spatial.ConvexHull(points=np.array(array_kept).T, qhull_options='QJ')
    return hull


def display_volumes(participants_hull, title, nb_episodes, participant_hull_ref=None, y_min=0, y_max=120):
    mean = []
    plt.close()
    if participant_hull_ref:
        for participant_key, value in participant_hull_ref.items():
            plt.plot([i for i in range(len(value))], value.values(), '-o', linewidth='0.4', alpha=0.3, color='grey')
    for participant_key, value in participants_hull.items():
        plt.plot([i for i in range(len(value))], value.values(), '-o', label=participant_key)
        # if len(value) == nb_blocks:
        #     mean.append([val for key, val in value.items()])
    # plt.plot([i for i in range(nb_blocks)], np.mean(mean, axis=0), 'o', linestyle='solid', color='red')
    plt.xticks([0, 5, 10, 15, 20], [i * nb_episodes for i in [0, 5, 10, 15, 20]])
    # plt.yticks([i * 10 for i in range(0, 13)])
    plt.ylim(y_min, y_max)
    plt.title(title)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.show()
    plt.savefig(f'{title}.png', bbox_inches="tight")
    plt.close()


def get_participants_hypercube_per_session(episodes):
    """ Iter through all participants to retrieve the array of all hypercube volumes per sessions"""
    hull_volume_per_participant = {}
    for participant, participant_sessions in episodes.items():
        hull_volume_per_participant[participant.user.username] = get_participant_hypercube_volume(participant_sessions)
    return hull_volume_per_participant


def get_participant_hypercube_volume(participant_sessions):
    """
    For a given participant, for all sessions retrieve first the hull and then the volumes for each session
    """
    max_target, max_speed, max_tracking, max_probe, max_radius = 7, 5, 6, 6, 0.6
    max_volume = max_target * max_speed * max_tracking * max_probe * max_radius
    hypercubes_volume = {}
    for session_id, session_points in participant_sessions.items():
        if len(session_points) > 5:
            session_hypercubes = get_all_hypercubes_volumes_per_session(session_points)
            hypercubes_volume[session_id] = np.mean(session_hypercubes) / max_volume
    return hypercubes_volume


def get_all_hypercubes_volumes_per_session(session_points):
    # Hyperparameters of probe and radius (to have axis in same order)
    max_probe_time = 12
    max_radius = 1.2
    # Map each episodes to a corresponding hypercube hypervolume
    episode_array = list(
        map(lambda episode: episode.n_targets * episode.speed_max * episode.tracking_time * (
                max_probe_time - episode.probe_time) * (max_radius - episode.radius), session_points))
    return episode_array


# ######################################################################################################################
# Let's display all the data:
def display_participants_success_ps(participants_success_ps, participant_success_ref=None, condition='zpdes',
                                    nb_episodes=50, success_type_title="binary", participant_std=None):
    fig = plt.figure()
    nb_values_max = 0
    if participant_success_ref:
        for participant, participant_sessions in participant_success_ref.items():
            points = participant_sessions.values()
            plt.plot([i for i in range(len(points))], points, '-o', linewidth='0.4', alpha=0.3, color='grey')
            if len(points) > nb_values_max:
                nb_values_max = len(points)
    if participant_std:
        for (participant, participant_sessions), (participant_std, participant_sessions_std) in zip(
                participants_success_ps.items(), participant_std.items()):
            points_std = np.array(list(participant_sessions_std.values()))
            points = participant_sessions.values()
            plt.plot([i for i in range(len(points))], points, 'o', linestyle='solid', label=participant.user.username)
            plt.fill_between([i for i in range(len(points))],
                             np.array(list(participant_sessions.values())) - points_std,
                             np.array(list(participant_sessions.values())) + points_std, alpha=0.3)
            if len(points) > nb_values_max:
                nb_values_max = len(points)
    else:
        for participant, participant_sessions in participants_success_ps.items():
            points = participant_sessions.values()
            plt.plot([i for i in range(len(points))], points, 'o', linestyle='solid', label=participant.user.username)
            if len(points) > nb_values_max:
                nb_values_max = len(points)

    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xticks([i for i in range(nb_values_max)], [str(i * nb_episodes) for i in range(1, nb_values_max + 1)],
               rotation=45)
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.title(f'{success_type_title}: ' + condition + ' ntargets=All')
    plt.savefig(f'SR_{condition}_{nb_episodes}_{success_type_title}', bbox_inches="tight")
    # plt.show()


def display_mean_zpdes_vs_baseline(zpdes, baseline, title, nb_blocks=5, fill_std=False):
    mean_zpdes, std_zpdes = compute_mean_std(zpdes, nb_blocks=nb_blocks)
    mean_baseline, std_baseline = compute_mean_std(baseline, nb_blocks=nb_blocks)
    plt.figure()
    plt.plot([i for i in range(len(mean_zpdes))], mean_zpdes, marker='D', linestyle='solid', linewidth=5, label='zpdes',
             color='red')

    plt.plot([i for i in range(len(mean_baseline))], mean_baseline, marker='D', linestyle='solid', linewidth=5,
             label='baseline',
             color='blue')
    if fill_std:
        plt.fill_between([i for i in range(len(mean_zpdes))], mean_zpdes - std_zpdes, linestyle='solid', color='red',
                         alpha=0.1)
        plt.fill_between([i for i in range(len(mean_zpdes))], mean_zpdes + std_zpdes, linestyle='solid', color='red',
                         alpha=0.1)
        plt.fill_between([i for i in range(len(mean_baseline))], mean_baseline - std_baseline, linestyle='solid',
                         color='blue', alpha=0.1)
        plt.fill_between([i for i in range(len(mean_baseline))], mean_baseline + std_baseline, linestyle='solid',
                         color='blue', alpha=0.1)
    else:
        for key_participant, value in zpdes.items():
            value = [val for val in list(value.values())]
            plt.plot([i for i in range(len(value))], value, '-o', linewidth='0.5', alpha=0.3,
                     color='red')
        for key_participant, value in baseline.items():
            value = [val for val in list(value.values())]
            plt.plot([i for i in range(len(value))], value, '-o', linewidth='0.5', alpha=0.3,
                     color='blue')
    plt.legend()
    plt.title(title)
    plt.savefig(f'{title}.png', bbox_inches="tight")
    plt.close()


def compute_mean_std(condition, nb_blocks=8):
    trans_data = []
    for participant, sessions in condition.items():
        tmp_parti = list(sessions.values()) + [0] * (nb_blocks - len(sessions.values()))
        trans_data.append(tmp_parti)
    # trans_data = np.array(trans_data)
    # nb_participants_per_session = [np.sum(np.array(trans_data)[:, i] > 0) for i in range(nb_blocks)]
    # mean_session = np.divide(np.sum(trans_data, axis=0), nb_participants_per_session)
    # return np.mean(trans_data, axis=0), np.std(trans_data, axis=0)
    return np.mean(np.array(trans_data), axis=0), np.array([np.std(np.array(elt), axis=0) for elt in trans_data])


def display_histo_frequency_ntargets(participants_frequency, nb_episodes, participants_nb_per_block, group):
    if not os.path.isdir('../../../outputs/v3_utl/v1/frequency_prolific_histo'): os.mkdir(
        '../../../outputs/v3_utl/v1/frequency_prolific_histo')
    for participant, frequency_sessions in participants_frequency.items():
        plt.figure()
        plt.title(f"n_targets distribution through time : \n {participant} \n group {group}")
        barwidth = 0.1
        # shift = np.linspace(-(len(frequency_sessions) / 2) * 0.1, (len(frequency_sessions) / 2) * 0.1, len(frequency_sessions))
        # shift = np.linspace(-0.3, 0.3, 8)
        shift = [-0.4, -0.25, -0.1, 0.05, 0.20, 0.35, 0.50]
        for session_index, (session_id, freqs) in enumerate(frequency_sessions.items()):
            plt.bar([session_index + shift[i] for i in range(len(freqs))], freqs, width=barwidth, label=session_id)
        # plt.legend()
        xticks_labels = []
        sum = 0
        for index, session_id in enumerate(participants_nb_per_block[participant].keys(), 1):
            sum += participants_nb_per_block[participant][session_id]
            xticks_labels.append(sum)
        plt.xticks([i for i in range(len(frequency_sessions))], xticks_labels)
        plt.tight_layout()
        plt.savefig(f"outputs/frequency/{participant}.png")
        plt.close()


def display_frequency_ntargets(participants_frequency, nb_episodes, participants_nb_per_block, group):
    if not os.path.isdir('../../../outputs/v3_utl/v1/frequency_prolific_histo'): os.mkdir(
        '../../../outputs/v3_utl/v1/frequency_prolific_histo')
    for participant, frequency_sessions in participants_frequency.items():
        plt.figure()
        plt.title(f"n_targets distribution through time : \n {participant} \n group {group}")
        barwidth = 0.1
        # shift = np.linspace(-(len(frequency_sessions) / 2) * 0.1, (len(frequency_sessions) / 2) * 0.1, len(frequency_sessions))
        # shift = np.linspace(-0.3, 0.3, 8)
        shift = [-0.4, -0.25, -0.1, 0.05, 0.20, 0.35, 0.50]
        session_id = [i for i in range(len(frequency_sessions))]
        values = np.array(list(frequency_sessions.values()))
        for i in range(5, -1, -1):
            plt.plot(session_id, np.squeeze(values[:, i]), label=i, marker='*')
        plt.legend()
        xticks_labels = []
        sum = 0
        for index, session_id in enumerate(participants_nb_per_block[participant].keys(), 1):
            sum += participants_nb_per_block[participant][session_id]
            if index % 2 == 0:
                xticks_labels.append(sum)
            else:
                xticks_labels.append(" ")
        plt.xticks([i for i in range(len(frequency_sessions))], xticks_labels)
        plt.yticks(np.arange(0, 1.1, 0.1))
        plt.tight_layout()
        savedir = "outputs/frequency_normalized/"
        Path(savedir).mkdir(parents=True, exist_ok=True)
        plt.savefig(f"outputs/frequency_normalized/{participant}.png")
        plt.close()


def display_average_activity(participants_average_activity):
    angles = [2 * math.pi / n for n in range(1, 6)]
    angles += [angles[0]]
    categories = ['session_id', 'speed', 'tracking_time', 'probe_duration', 'radius']
    for participant, average_activities in participants_average_activity.items():
        fig, axs = plt.subplots(3, 2, subplot_kw={'projection': 'polar'}, constrained_layout=True)
        fig.suptitle(participant.user.username)
        for i, ax in enumerate(axs.flat):
            if int(i + 2) in average_activities:
                ax.set_xticklabels(categories)
                chart_values = list(average_activities[i + 2].values())
                for session_idx, session in enumerate(chart_values):
                    line = [session_idx] + session + [session_idx]
                    ax.plot(angles, line, linewidth=1, linestyle='solid')
            else:
                # This target nb has not been proposed to the participant
                pass
        plt.show()


# ######################################################################################################################
# This is for ZPDES trajectory internal states:
def list_division(list, scalar):
    return [elt / scalar for elt in list]


def normalize(lists_values):
    return list(map(lambda list_values: list_division(list_values, sum(lists_values)), lists_values))


def reformat_matrix(matrix):
    """ Just for visualization purposes """
    # Insert columns:
    matrix = np.insert(matrix, 7, -np.ones((1, 6)), axis=1)
    matrix = np.insert(matrix, 15, -np.ones((1, 6)), axis=1)
    matrix = np.insert(matrix, 23, -np.ones((1, 6)), axis=1)
    # Insert row:
    for i in range(5, 0, -1):
        matrix = np.insert(matrix, i, -np.ones((1, 31)), axis=0)
    return matrix


def save_matrix(matrix, participant, episode_number):
    plt.imshow(matrix)
    plt.title(f"Episode nb: {episode_number}")
    plt.set_cmap("Greens")
    plt.colorbar()
    plt.clim(-1, 1)
    plt.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False)
    plt.yticks(np.arange(11), ('0', '', '1', '', '2', '', '3', '', '4', '', '5'))
    plt.savefig(f'outputs_results/{participant.user.username}/{episode_number}.png')
    plt.close()


def get_matrix_bandvals(dict_vals):
    raw_matrix = []
    for key, values in dict_vals.items():
        raw_matrix += [values]
    proba_matrix = []
    for row in raw_matrix:
        tmp_row = []
        for col in row:
            tmp_row += [list_division(col, sum(col))]
        proba_matrix += [copy.deepcopy(tmp_row)]
    # proba_matrix = list(map(lambda lists_values: normalize(lists_values), raw_matrix))
    main_raw = raw_matrix.pop(0)
    main_proba = proba_matrix.pop(0)
    main_matrix = np.zeros((6, 6))
    np.fill_diagonal(main_matrix, main_proba)
    proba_matrix = np.matmul(main_matrix, np.array(proba_matrix).reshape((6, 28)))
    proba_matrix = reformat_matrix(proba_matrix)
    return proba_matrix


def get_matrices(all_episodes):
    saved_zpdes_participants = pd.DataFrame(
        columns=['participant', 'episode', 'main_index', 'main_value', 'main_success', 'speed_values',
                 'tracking_duration_values',
                 'probe_duration_values', 'radius_values', 'speed_success', 'tracking_duration_success',
                 'probe_duration_success', 'radius_success', 'episode_sample', 'results'])
    for participant, sessions in all_episodes.items():
        participant_wrapper = MotParamsWrapper(participant)
        participant_zpdes = k_lib.seq_manager.ZpdesHssbg(zpdes_params)
        participant_matrix = []
        # if not os.path.isdir(f"outputs_results/{participant.user.username}"):
        #     os.mkdir(f"outputs_results/{participant.user.username}")
        for session_key, session_episodes in sessions.items():
            for episode_nb, episode in enumerate(session_episodes):
                # Status of zpdes at that time step
                # bandvals = {
                #     SSBG_key: [(SSB.bandval, parse_success_into_ALP(SSB.success, SSB.bandval)) for SSB in SSBG.SSB] for
                #     SSBG_key, SSBG in participant_zpdes.SSBGs.items()}
                bandvals = {
                    SSBG_key: [(SSB.bandval, get_SR(SSB.success)) for SSB in SSBG.SSB] for
                    SSBG_key, SSBG in participant_zpdes.SSBGs.items()}
                episode_summary = get_row_for_zpdes_csv(participant, episode, bandvals, participant_wrapper)
                # Feed results of past exercices
                # matrix = get_matrix_bandvals(bandvals)
                # save_matrix(matrix, participant, episode.episode_number)
                saved_zpdes_participants = saved_zpdes_participants.append(copy.deepcopy(episode_summary),
                                                                           ignore_index=True)
                participant_wrapper.update(episode, participant_zpdes)
                # check_ALP(participant_zpdes, bandvals)
        print(participant)
        # create_gif()
    saved_zpdes_participants.to_csv('zpdes_states_exploration.csv')


def get_LP_trajectory(all_episodes, get_reward, LP_type, group, add_trajectory=False, get_current=False,
                      keep_history=False):
    create_folder(["trajectories"], root=None)
    create_folder(["baseline", "zpdes"], root="trajectories")
    create_folder(["n_targets", "speed", "tracking", "probe", "radius"], root="trajectories/zpdes")
    create_folder(["n_targets", "speed", "tracking", "probe", "radius"], root="trajectories/baseline")
    values = {'n_targets': np.array([2, 3, 4, 5, 6, 7], dtype=float),
              'speed_max': np.array([2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0], dtype=float),
              'tracking_time': np.array([3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0], dtype=float),
              'probe_time': np.array([12.0, 11.0, 10.0, 9.0, 8.0, 7.0, 6.0], dtype=float),
              'n_distractors': np.linspace(14, 7, 8, dtype=float),
              'radius': np.array([1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.6], dtype=float)}
    for participant, sessions in all_episodes.items():
        # Init all placeholders for data trajectories:
        participant_targets_history = [[] for i in range(6)]
        participant_targets_LP = [[0 for i in range(6)]]
        participant_subdims_history = {
            'speed': [[[] for i in range(7)] for i in range(6)],
            'tracking': [[[] for i in range(7)] for i in range(6)],
            'probe': [[[] for i in range(7)] for i in range(6)],
            'radius': [[[] for i in range(7)] for i in range(6)]}
        participant_subdims_LP = {
            'speed': [[[0 for i in range(7)]] for i in range(6)],
            'tracking': [[[0 for i in range(7)]] for i in range(6)],
            'probe': [[[0 for i in range(7)]] for i in range(6)],
            'radius': [[[0 for i in range(7)]] for i in range(6)]}
        n_targets = []
        # Get a nice structure of the player's history and update LP
        episode_step = 0
        for session_key, session_episodes in sessions.items():
            for episode in session_episodes:
                episode_step += 1
                # Parse episode real values into index:
                mapped_episode = map_episode(episode, values)
                # Get a reward from episode
                score = get_reward(episode)
                # Store this reward into an array for n_targets
                participant_targets_history[mapped_episode[0]].append(score)
                # Store this reward into a dict for sub parameters:
                for ii, sub_dim_key in enumerate(participant_subdims_history.keys()):
                    # mapped_episode[0] = corresponding n_targets
                    # mapped_episode[ii] correct subvalue
                    participant_subdims_history[sub_dim_key][mapped_episode[0]][mapped_episode[ii + 1]].append(score)
                # Update LP:
                participant_targets_LP, participant_subdims_LP = update_LP_values(mapped_episode,
                                                                                  participant_targets_LP,
                                                                                  participant_targets_history,
                                                                                  participant_subdims_LP,
                                                                                  participant_subdims_history,
                                                                                  get_current=get_current,
                                                                                  keep_history=keep_history)
                # print(episode_step)
                # print("n_target=", mapped_episode[0], " result=", episode.get_results)
                # for i in range(6):
                #     history_LP = [participant_targets_LP[j][i] for j in range(len(participant_targets_LP))]
                #     if len(participant_targets_history[i]) > 10:
                #         history = participant_targets_history[i][-10:]
                #         print(i, history_LP[-1], "recent:", history[-10 // 2:], "old", history[:10 // 2], "all:", history)
                #     else:
                #         print(i, participant_targets_history[i], history_LP[-1])
                # Also store the nb_target lvl proposed (to plot lines on the graph)
                # n_targets.append((mapped_episode[0], episode.get_results))
                n_targets.append(mapped_episode[0])
        if not add_trajectory:
            n_targets = None
        bounds = list(np.arange(0, 5, 0.5))
        bounds.insert(0, -1)
        plot_matrice_LP(participant_targets_LP, participant_name=participant, LP_type=LP_type, trajectory=n_targets,
                        bounds=bounds, group=group)
        for key, data in participant_subdims_LP.items():
            for main_dim_index, LP in enumerate(data):
                plot_matrice_LP(LP, participant_name=participant, LP_type=LP_type, group=group, parameter=key,
                                main_dim=str(main_dim_index), nb_class=7)


def create_folder(folder_list, root=None):
    for name in folder_list:
        if name not in os.listdir(root):
            if root:
                os.mkdir(f"{root}/{name}")
            else:
                os.mkdir(name)


def update_LP_values(mapped_episode, participant_targets_LP, participant_targets_history,
                     participant_subdims_LP, participant_subdims_history, get_current=False, keep_history=False):
    # Retrieve last LP and copy all values into new array and concatenate it to LP history objects:
    participant_targets_LP.append(copy.deepcopy(participant_targets_LP[-1]))
    # Then compute empirical LP :
    participant_targets_LP[-1][mapped_episode[0]] = compute_ES_LP(participant_targets_history[mapped_episode[0]])
    # Same for subdims:
    previous_LP_subdims = {}
    for ii, (key, array) in enumerate(participant_subdims_LP.items()):
        # For all values of n_targets, copy the last
        for i in range(len(array)):
            participant_subdims_LP[key][i].append(copy.deepcopy(array[i][-1]))
        # participant_subdims_LP[key][mapped_episode[0]].append(copy.deepcopy(array[mapped_episode[0]][-1]))
        participant_subdims_LP[key][mapped_episode[0]][-1][mapped_episode[ii + 1]] = compute_ES_LP(
            participant_subdims_history[key][mapped_episode[0]][mapped_episode[ii + 1]])
    if get_current:
        participant_targets_LP[-1][mapped_episode[0]] = get_current_state(
            participant_targets_history[mapped_episode[0]])
    if not keep_history:
        for i in range(6):
            if i != mapped_episode[0]:
                participant_targets_LP[-1][i] = 0
    return participant_targets_LP, participant_subdims_LP


def compute_ES_LP(history_array):
    """Compute empirical absolute LP"""
    window_min, window_max = 2, 10
    length = len(history_array)
    if length < window_min:
        return 0
    elif length >= window_max:
        history_array = history_array[-10:]
        length = 10
    alp = np.abs(np.mean(history_array[-length // 2:]) - np.mean(history_array[:length // 2]))
    # normalized_alp = alp / len(history_array[-length // 2:])
    # if normalized_alp > 1:
    #     print("problemos")
    # return normalized_alp
    return alp


def get_current_state(history_array):
    return history_array[-1]


def map_episode(episode, values):
    speed_i = np.where(values['speed_max'] == float(episode.speed_max))[0][0]
    n_targets_i = np.where(values['n_targets'] == float(episode.n_targets))[0][0]
    track_i = np.where(values['tracking_time'] == float(episode.tracking_time))[0][0]
    probe_i = np.where(values['probe_time'] == float(episode.probe_time))[0][0]
    radius_i = np.where(values['radius'] == float(episode.radius))[0][0]
    return [n_targets_i, speed_i, track_i, probe_i, radius_i]


def extract_binary_format(episode):
    if episode.get_results != 1:
        return 0.5
    return episode.get_results


def extract_binary(episode):
    return episode.get_results


def extract_F1(episode):
    nb_missed_targets = episode.n_targets - episode.nb_target_retrieved
    nb_missed_distrac = 16 - episode.n_targets - episode.nb_distract_retrieved
    # Within everything that has been predicted as a positive, precision counts the percentage that is correct:
    # TP / (TP + FP)
    if (episode.nb_target_retrieved + nb_missed_distrac) == 0:
        precision = 0
    else:
        precision = episode.nb_target_retrieved / (episode.nb_target_retrieved + nb_missed_distrac)
    # Within everything that actually is positive, how many did the model succeed to find:
    # TP / (TP + FN)
    if (episode.nb_target_retrieved + nb_missed_targets) == 0:
        recall = 0
    else:
        recall = episode.nb_target_retrieved / (episode.nb_target_retrieved + nb_missed_targets)
    if precision + recall == 0:
        f1_score = 0
    else:
        f1_score = 2 * (precision * recall) / (precision + recall)
    return f1_score


def extract_recall(episode):
    nb_missed_targets = episode.n_targets - episode.nb_target_retrieved
    if (episode.nb_target_retrieved + nb_missed_targets) == 0:
        recall = 0
    else:
        recall = episode.nb_target_retrieved / (episode.nb_target_retrieved + nb_missed_targets)
    return recall


def get_customized_cmap():
    cmap = plt.cm.get_cmap('jet')
    colors_ = cmap(np.arange(cmap.N))
    colors_[0, :] = [0, 0, 0, 1]
    colors_[1, :] = [255, 255, 255, 1]
    return LinearSegmentedColormap.from_list(cmap.name + "_gray", colors_, cmap.N)


def plot_matrice_LP(participant_LP, participant_name, LP_type, bounds=None, trajectory=None, parameter="n_targets",
                    group="zpdes",
                    main_dim="main", nb_class=6):
    plt.close()
    plt.rcParams["figure.figsize"] = (20, 3)
    img = []
    height_per_class = 50
    hline_size = 3
    total_height = (nb_class * height_per_class) + (nb_class * hline_size)
    tick_step = height_per_class // 2
    for episode in participant_LP:
        episode_reformat = []
        for value in episode:
            if value == 0:
                if type(value) == int:
                    value = 2
                else:
                    value += 0.000001
            for i in range(height_per_class):
                episode_reformat.append(value)
            for i in range(hline_size):
                episode_reformat.append(-1)
        # img.append([-1 for i in range(len(episode_reformat))])
        img.append(episode_reformat)
    # convert to rgba:
    img = np.array(img).T
    # # make a color map of fixed colors
    # colors_list = ['black', 'white', 'bisque', 'moccasin', 'lightyellow', 'yellow', 'greenyellow', 'chartreuse',
    #                'lawngreen', 'palegreen', 'lightgreen', 'orange', 'lightcoral', 'indianred',
    #                'firebrick', 'red', 'darkmagenta', 'purple', 'indigo', 'blue']
    # cmap = colors.ListedColormap(colors_list)
    # Default bounds:
    # if not bounds:
    #     bounds = [-1, 0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 0.8, 0.9]
    # bounds = list(np.arange(0, 1, 0.05))
    # bounds.insert(0, -1)
    # bounds = [-1, 0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.8, 0.9,
    #           1]
    # norm = colors.BoundaryNorm(bounds, cmap.N)
    y_ticks_array = []
    for i in range(0, nb_class):
        y_ticks_array.append(tick_step + (i * height_per_class))
    # tell imshow about color map so that only set colors are used
    if parameter == 'main':
        plt.yticks(y_ticks_array, [f"nb-{i}" for i in range(2, nb_class + 2)])
    else:
        plt.yticks(y_ticks_array, [f"lvl-{i}" for i in range(nb_class)])
    # plt.imshow(img, interpolation='nearest', origin='lower', cmap=cmap, norm=norm)
    # plt.imshow(img, interpolation='nearest', origin='lower', cmap="plasma", vmin=0, vmax=1)
    my_cmap = matplotlib.cm.get_cmap('viridis')
    my_cmap.set_under('black')
    my_cmap.set_over('w')
    plt.imshow(img, interpolation='nearest', origin='lower', cmap=my_cmap, vmax=1, vmin=0)
    # cbar = plt.colorbar(ticks=bounds[1:])
    cbar = plt.colorbar()
    if trajectory:
        # plt.plot([i for i in range(len(trajectory))], list(map(lambda x: 25 + (x) * 50, trajectory)), linewidth=0.5, c='white')
        plt.scatter(x=[i for i in range(len(trajectory))], y=list(map(lambda x: 25 + (x) * 50, trajectory)), marker='.',
                    c='white', edgecolors='k')
    # cbar.ax.set_yticklabels([''])
    # plt.show()
    create_folder([f"{participant_name}"], root=f"trajectories/{group}/{parameter}")
    plt.savefig(f"trajectories/{group}/{parameter}/{participant_name}/{participant_name}_{LP_type}_{main_dim}.png")


def get_SR(success_list):
    # To get mean performance:
    # return [np.mean(value_list_success) if len(value_list_success) > 0 else 0 for value_list_success in sucess_list]
    filter = 0.8
    return [filter * compute_ES_LP(value_list_success) if len(value_list_success) > 0 else 0 for value_list_success in
            success_list]


def get_entropy(episodes):
    participants_entropy = {}
    dims = ['MAIN', 'nb2', 'nb3', 'nb4', 'nb5', 'nb6', 'nb7']
    for participant, dict_values in episodes.items():
        participant_wrapper = MotParamsWrapper(participant)
        participant_zpdes = k_lib.seq_manager.ZpdesHssbg(zpdes_params)
        participants_entropy[participant] = {}
        for session_key, session_episodes in dict_values.items():
            for episode in session_episodes:
                # Status of zpdes at that time step
                bandval_main = np.array(participant_zpdes.SSBGs['MAIN'].SSB[0].bandval)
                open_values = dims[0:len(bandval_main[bandval_main != 0]) + 1]
                for SSBG_key in open_values:
                    SSBG = participant_zpdes.SSBGs[SSBG_key]
                    if SSBG_key not in participants_entropy[participant]:
                        participants_entropy[participant][SSBG_key] = {}
                    for SSB_index, SSB in enumerate(SSBG.SSB):
                        if f"{SSBG_key}_{SSB_index}" not in participants_entropy[participant][SSBG_key]:
                            participants_entropy[participant][SSBG_key][f"{SSBG_key}_{SSB_index}"] = []
                        distrib = parse_quality_to_distribution(SSB.bandval)
                        distrib = distrib[distrib != 0]
                        entropy = get_entropy_from_distribution(distrib)
                        if len(distrib) == 1:
                            normalized_entropy = 1
                        else:
                            normalized_entropy = entropy / np.log10(len(distrib))
                        participants_entropy[participant][SSBG_key][f"{SSBG_key}_{SSB_index}"].append(
                            normalized_entropy)
                participant_wrapper.update(episode, participant_zpdes)
    return participants_entropy


def parse_quality_to_distribution(bandval):
    return np.array(bandval) / sum(bandval)


def get_entropy_from_distribution(distrib):
    return -sum(distrib * np.log10(distrib))


def baseline_csv(episodes):
    baseline_participants = pd.DataFrame(
        columns=['participant', 'episode', 'main_index', 'episode_sample', 'results'])
    for participant, dict_values in episodes.items():
        participant_wrapper = MotParamsWrapper(participant)
        print(participant)
        for session_key, session_episodes in dict_values.items():
            for episode in session_episodes:
                # Status of zpdes at that time step
                episode_summary = {'participant': participant.user.username}
                episode_summary['episode'] = episode.episode_number
                ep = participant_wrapper.parse_activity(episode)['act']
                episode_summary['main_index'] = ep['MAIN'][0]
                episode_summary['episode_sample'] = ep
                episode_summary['results'] = episode.get_results
                baseline_participants = baseline_participants.append(copy.deepcopy(episode_summary),
                                                                     ignore_index=True)
    baseline_participants.to_csv('baseline_states.csv')


def check_ALP(participant_zpdes, bandvals):
    newbandvals = {SSBG_key: [SSB.bandval for SSB in SSBG.SSB] for SSBG_key, SSBG in
                   participant_zpdes.SSBGs.items()}
    for key in bandvals.keys():
        for sub_dim_old, sub_dim_new in zip(bandvals[key], newbandvals[key]):
            assert_calcul(sub_dim_old[0], sub_dim_old[1], sub_dim_new)


def create_gif():
    print('creating gif\n')
    filenames = [f"outputs_results/Axelle/{i}.png" for i in range(852)]
    with imageio.get_writer(f'Axelle.gif', mode='I') as writer:
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)
    print('gif complete\n')


def parse_success_into_ALP(success_list, bandval):
    stepUpdate = 10
    alp = []
    for index_dim, dim_value in enumerate(success_list):
        if len(dim_value) > 2:
            y_step = min(stepUpdate, len(dim_value))
            # y_range = old_div(y_step, 2)
            y_range = y_step // 2
            sum_old = np.mean(dim_value[-y_step:-y_range])
            # print "sum_old", sum_old
            sum_recent = np.mean(dim_value[-y_range:])
            r = abs(sum_recent - sum_old)
            alp.append(r)
        else:
            if bandval[index_dim] > 0:
                alp.append(0.05)
            else:
                alp.append(0)
    return alp


def assert_calcul(oldbanditval, reward, banditval):
    """
        Function to check that ALP computed makes sens :)
    """
    filter1 = 0.2
    filter2 = 0.8
    if not all(
            np.isclose(np.array(banditval), filter1 * np.array(reward) + filter2 * np.array(oldbanditval), rtol=1e-10)):
        print(oldbanditval, banditval)


def get_row_for_zpdes_csv(participant, episode, bandvals, wrapper):
    episode_summary = []
    for main_index, main_value in enumerate(bandvals['MAIN'][0][0]):
        participant_row = {'participant': participant.user.username}
        participant_row['episode'] = episode.episode_number
        participant_row['main_index'] = main_index
        participant_row['main_value'] = main_value
        participant_row['main_success'] = copy.deepcopy(bandvals[f'MAIN'][0][1][main_index])
        participant_row['speed_values'] = copy.deepcopy(bandvals[f'nb{main_index + 2}'][0][0])
        participant_row['speed_success'] = copy.deepcopy(bandvals[f'nb{main_index + 2}'][0][1])
        participant_row['tracking_duration_values'] = copy.deepcopy(bandvals[f'nb{main_index + 2}'][1][0])
        participant_row['tracking_duration_success'] = copy.deepcopy(bandvals[f'nb{main_index + 2}'][1][1])
        participant_row['probe_duration_values'] = copy.deepcopy(bandvals[f'nb{main_index + 2}'][2][0])
        participant_row['probe_duration_success'] = copy.deepcopy(bandvals[f'nb{main_index + 2}'][2][1])
        participant_row['radius_values'] = copy.deepcopy(bandvals[f'nb{main_index + 2}'][3][0])
        participant_row['radius_success'] = copy.deepcopy(bandvals[f'nb{main_index + 2}'][3][1])
        participant_row['episode_sample'] = wrapper.parse_activity(episode)['act']
        participant_row['results'] = episode.get_results
        episode_summary.append(participant_row)
    return pd.DataFrame(episode_summary)


def exclude_participant(dict_group, nb_blocks):
    return {participant_index: participant_sessions_dict for participant_index, participant_sessions_dict in
            dict_group.items() if len(participant_sessions_dict) >= nb_blocks}


def get_novelty(group):
    novelties_metric = {}
    for participant_id, participant_sessions in group.items():
        novelties_metric[participant_id] = {}
        for session_id, session_values in participant_sessions.items():
            episode_array = list(
                map(lambda episode: [episode.n_targets, episode.speed_max, episode.tracking_time, episode.probe_time,
                                     episode.radius],
                    session_values))
            nb_tot = len(episode_array)
            unique = len(np.unique(np.array(episode_array), axis=0))
            print(participant_id, session_id, nb_tot, unique)
            if nb_tot > 0:
                novelties_metric[participant_id][session_id] = unique / nb_tot
    return novelties_metric


def get_feature_from_sessions(group, feature_extractor):
    idle_metric = {}
    for participant_id, participant_sessions in group.items():
        idle_metric[participant_id] = []
        for session_id, session_values in participant_sessions.items():
            episode_array = list(map(lambda episode: feature_extractor(episode), session_values))
            idle_metric[participant_id].append(np.mean(episode_array))
        idle_metric[participant_id] = np.mean(idle_metric[participant_id])
    return idle_metric


def get_len_session(group):
    idle_metric = {}
    for participant_id, participant_sessions in group.items():
        idle_metric[participant_id] = {}
        for session_id, session_values in participant_sessions.items():
            idle_metric[participant_id][session_id] = len(session_values)
    return idle_metric


def mean_nb_of_episode_in_study(study, nb_per_blocks):
    mean = []
    for participant, sessions in nb_per_blocks.items():
        sum = 0
        for session_id, nb_in_session in sessions.items():
            sum += nb_in_session
        print(f"Participant {participant} has played: {sum}")
        mean.append(sum)
    print(f"In study {study}, {np.mean(mean)} episodes were played. ")


def display_main_entropy(entropy_zpdes, entropy_zpdes_ref, nb_episodes):
    plt.close()
    means_windows = []
    if entropy_zpdes_ref:
        for participant, entropies in entropy_zpdes_ref.items():
            mean = average_window(entropies['MAIN']['MAIN_0'], nb_episodes)
            means_windows.append(mean)
        means, std = get_means_of_array_w_different_size(means_windows)
        plt.bar([i for i in range(len(means))], means, yerr=std, align='center', alpha=0.3, ecolor='grey', capsize=2)
    for participant, entropies in entropy_zpdes.items():
        mean = average_window(entropies['MAIN']['MAIN_0'], nb_episodes)
        plt.plot([i for i in range(len(mean))], mean, linewidth=3, marker='o', label=participant)
    # plt.legend()
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.title("Previous experiment represented in bars")
    plt.suptitle(f"Participants in ZPDES, \n Average normalized entropy on a window of {nb_episodes} nb_episodes")
    plt.tight_layout()
    plt.savefig("main_entropy.png")


def display_sub_dims_entropy(entropy_zpdes, entropy_zpdes_ref, nb_episodes):
    # Compute mean for zpdes_ref
    means_ref = {}
    for participant, entropies in entropy_zpdes_ref.items():
        for nb_target_key in entropies.keys():
            if nb_target_key != 'MAIN':
                for sub_dims_name, sub_dims_entropy in entropies[nb_target_key].items():
                    mean_sub_dim = average_window(sub_dims_entropy, nb_episodes)
                    if sub_dims_name not in means_ref:
                        means_ref[sub_dims_name] = [mean_sub_dim]
                    else:
                        means_ref[sub_dims_name].append(mean_sub_dim)
    # Then for new participants:
    means_new = {}
    for participant, entropies in entropy_zpdes.items():
        for nb_target_key in entropies.keys():
            if nb_target_key != 'MAIN':
                for sub_dims_name, sub_dims_entropy in entropies[nb_target_key].items():
                    mean = average_window(sub_dims_entropy, nb_episodes)
                    if sub_dims_name not in means_new:
                        means_new[sub_dims_name] = {}
                    means_new[sub_dims_name][participant] = mean
    subdims = ['speed', 'tracking_duration', 'probe_duration', 'radius']
    la = []
    # Display everything:
    for sub_dims_name, sub_dim in means_ref.items():
        plt.figure()
        means, std = get_means_of_array_w_different_size(sub_dim)
        if sub_dims_name in means_new:
            for participant, mean in means_new[sub_dims_name].items():
                la.append({sub_dims_name: mean})
                plt.plot([i for i in range(len(mean))], mean, linewidth=3, marker='o', label=participant)
        # plt.legend(loc='lower right')
        plt.title(f"Component : {sub_dims_name[:-2]} - {subdims[int(sub_dims_name[-1])]}")
        plt.suptitle(f"Participants in ZPDES, \n Average normalized entropy on a window of {nb_episodes} nb_episodes")
        plt.tight_layout()
        plt.bar([i for i in range(len(means))], means, align='center', alpha=0.3, ecolor='grey', capsize=2)
        plt.yticks(np.arange(0, 1.1, 0.1))
        # plt.show()
        plt.savefig(f"{sub_dims_name}-entropy.png")


def average_window(values, nb_episodes):
    return [np.mean(values[i:i + nb_episodes]) for i in range(0, len(values), nb_episodes)]


def get_means_of_array_w_different_size(means):
    sizes = [len(elt) for elt in means]
    max_size = np.max(sizes)
    return_means, return_stds = [], []
    for ii in range(max_size):
        col = []
        for elt in means:
            if ii < len(elt):
                col.append(elt[ii])
        return_means.append(np.mean(col))
        return_stds.append(np.std(col))
    return return_means, return_stds


def get_params_total_frequency(episodes_dict):
    return_dict, trajectory = {}, {}
    sub_dims = ['speed', 'tracking_duration', 'probe_duration', 'radius']
    main_dim_names = [f"nb{i}" for i in range(2, 8)]
    for participant, episodes_dict in episodes_dict.items():
        episode_nb = 0
        participant_wrapper = MotParamsWrapper(participant)
        return_dict[participant] = {nb_target: {sub_dim: np.zeros(7) for sub_dim in sub_dims} for nb_target in range(6)}
        trajectory[participant] = {nb_target: {sub_dim: np.zeros(7) for sub_dim in sub_dims} for nb_target in range(6)}
        for session_id, session_episodes in episodes_dict.items():
            for episode in session_episodes:
                episode_nb += 1
                parse_episode = participant_wrapper.parse_activity(episode)['act']
                main_dim = parse_episode['MAIN'][0]
                main_dim_name = main_dim_names[main_dim]
                for index, sub_dim in enumerate(sub_dims):
                    # If it's the first time to use this activity, store the episode_nb
                    if return_dict[participant][main_dim][sub_dim][parse_episode[main_dim_name][index]] == 0:
                        trajectory[participant][main_dim][sub_dim][parse_episode[main_dim_name][index]] = episode_nb
                    return_dict[participant][main_dim][sub_dim][parse_episode[main_dim_name][index]] += 1
    return return_dict, trajectory


def plot_params_total_frequency(frequency_dict, trajectory, nb_per_block, group):
    plt.close()
    label_loc = np.linspace(start=0, stop=360, num=5)
    positions = [i for i in range(0, 7)]
    target_mapper = [f"{i + 2} targets" for i in range(6)]
    cmap = matplotlib.cm.get_cmap('inferno')
    for (participant, episodes_dict), (_, trajectory_dict) in zip(frequency_dict.items(), trajectory.items()):
        trajectory_dict = {session_key: {dim: array for dim, array in session.items()} for session_key, session in
                           trajectory_dict.items()}
        plt.close()
        fig, axs = plt.subplots(2, 3, subplot_kw={'projection': 'polar'}, figsize=(15, 15), constrained_layout=True)
        nb_episodes_participant = sum(nb_per_block[participant].values())
        norm = plt.Normalize(0, nb_episodes_participant)
        for idx, ax in enumerate(axs.flat):
            ax.set_title(f'Dim {target_mapper[idx]}')
            ax.set_thetagrids(angles=label_loc, labels=['speed', 'tracking', 'probe', 'radius', 'speed'])
            ax.set_rgrids(range(0, 8), labels='')
            # Plot point per point:
            for position in positions:
                for (index, (key, dim)), (traj_key, dim_traj) in zip(enumerate(episodes_dict[idx].items()),
                                                                     trajectory_dict[idx].items()):
                    rgba = cmap(norm(dim_traj[position]))
                    ax.scatter(np.deg2rad(label_loc)[index], [position], c=[rgba], s=dim[position] * 10)
        sm = ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=axs[:, :], location='right', shrink=0.6)
        cbar.ax.set_title("Episode_nb")
        fig.savefig(f"{participant}-{group}.png")


def get_nb_episodes(sessions):
    return sum(dict(map(lambda item: (item[0], len(item[1])), sessions.items())).values())


def get_age(participant):
    return 2022 - int(Answer.objects.get(participant_id=participant.id, question__handle="prof-mot-12").value)


def get_study_duration(participant):
    return int(Answer.objects.get(participant_id=participant.id, question__handle="prof-mot-11").value)


def get_attention_deficit(participant):
    attention_responses = Answer.objects.filter(participant_id=participant.id, question__instrument="get_attention")
    attention_score = 0
    for index, resp in enumerate(attention_responses):
        if index < 3 and int(resp.value) > 2:
            attention_score += 1
        elif index >= 3 and int(resp.value) > 3:
            attention_score += 1
    return attention_score


def get_dict_mean_activity(episodes, session_id):
    return_dict = {}
    for participant, sessions in episodes.items():
        return_dict[participant] = get_mean_activity(sessions[list(sessions.keys())[session_id]])
    return return_dict


def get_mean_activity(session):
    mapped_array = np.array(list(
        map(lambda episode: [episode.n_targets, episode.speed_max, episode.tracking_time, episode.probe_time,
                             episode.radius], session)))
    return np.mean(mapped_array, axis=0)


def map_keys(dict):
    return {k.id: v for k, v in dict.items()}


def get_intra_evaluation(study, full_participant=True):
    all_binary, all_F1 = {}, {}
    stud = Study.objects.get(name=study)
    p = ParticipantProfile.objects.all().filter(study__name="v3_utl")
    df_F1, df_binary = pd.DataFrame(columns=["participant_id", "condition", "s_0", "s_1", "s_2", "s_3"]), pd.DataFrame(
        columns=["participant_id", "condition", "s_0", "s_1", "s_2", "s_3"])
    for participant in p:
        episodes = Episode.objects.all().filter(participant=participant.user).filter(is_training=False)
        # Only takes participant that did the whole training:
        if len(episodes) == 200:
            dict_info = {"participant_id": participant.user.id, "condition": participant.extra_json['condition']}
            # Map episodes to results:
            binary_results = get_binary_results(episodes)
            F1_results = get_F1_results(episodes)
            # Map episodes to session and to mean per session:
            mean_binary = [np.mean(binary_results[step: step + 50]) for step in range(0, 151, 50)]
            mean_F1 = [np.mean(F1_results[step: step + 50]) for step in range(0, 151, 50)]
            # all_binary[participant.id] = {f"s_{i}": mean_binary[i] for i in range(len(mean_binary))}
            # all_F1[participant.id] = {f"s_{i}": mean_F1[i] for i in range(len(mean_F1))}
            df_F1.loc[len(df_F1)] = {**dict_info, **{f"s_{i}": mean_F1[i] for i in range(len(mean_F1))}}
            df_binary.loc[len(df_binary)] = {**dict_info, **{f"s_{i}": mean_binary[i] for i in range(len(mean_binary))}}
    df_F1.to_csv(f"{study}_F1_intra.csv", index=False)
    df_binary.to_csv(f"{study}_binary_intra.csv", index=False)


def get_binary_results(episodes):
    return [ep.get_results for ep in episodes]


def get_F1_results(episodes):
    return [ep.get_F1_score for ep in episodes]


if __name__ == '__main__':
    get_volume, get_frequency_radar_plots, get_zpdes_entropy, get_frequency_histograms = True, True, True, True
    get_accuracy, get_summary_trajectories, get_novelty_trajectories, create_ID_csv = True, True, True, True
    get_lp_traj = True
    get_intra_eval = True
    study = "v3_utl"
    nb_episodes = 100
    dir_path = "../../../static/JSON/config_files"
    zpdes_params = func.load_json(file_name='ZPDES_mot', dir_path=dir_path)
    # #########################################################################################################@
    # (1) Get episodes
    # #########################################################################################################@
    nb_participants, nb_participants_in, nb_baseline, nb_zpdes, descriptive_dict, zpdes_participants, \
        baseline_participants = get_exp_status(study)
    all_episodes, true_episodes, nb_per_blocks, nb_per_blocks_true = get_true_episodes(zpdes_participants,
                                                                                       nb_episodes=nb_episodes,
                                                                                       keep_ntargets=None)
    # get_LP_trajectory(all_episodes, extract_F1, LP_type="F1_int_with_trajectory", group="zpdes")
    baseline_episodes, baseline_true_episodes, baseline_nb_per_blocks, baseline_nb_per_blocks_true = get_true_episodes(
        baseline_participants,
        nb_episodes=nb_episodes,
        keep_ntargets=None)

    if get_intra_eval:
        get_intra_evaluation(study)

    if get_lp_traj:
        print("PLOT ZPDES")
        get_LP_trajectory(all_episodes, extract_F1, LP_type="F1_score", group="zpdes",
                          add_trajectory=False,
                          get_current=False, keep_history=True)
        get_LP_trajectory(all_episodes, extract_recall, LP_type="Recall_score", group="zpdes",
                          add_trajectory=False,
                          get_current=False, keep_history=True)
        get_LP_trajectory(all_episodes, extract_binary, LP_type="Binary_score", group="zpdes",
                          add_trajectory=False,
                          get_current=False, keep_history=True)
        print("PLOT BASELINE")
        get_LP_trajectory(baseline_episodes, extract_F1, LP_type="F1_score", group="baseline",
                          add_trajectory=False,
                          get_current=False, keep_history=True)
        get_LP_trajectory(baseline_episodes, extract_recall, LP_type="Recall_score", group="baseline",
                          add_trajectory=False,
                          get_current=False, keep_history=True)
        get_LP_trajectory(baseline_episodes, extract_binary, LP_type="Binary_score", group="baseline",
                          add_trajectory=False,
                          get_current=False, keep_history=True)

    # nb_participants_axa, nb_participants_in_axa, nb_baseline_axa, nb_zpdes_axa, descriptive_dict_axa, zpdes_participants_axa, \
    # baseline_participants_axa = get_exp_status("v0_axa")
    # nb_participants_ubx, nb_participants_in_ubx, nb_baseline_ubx, nb_zpdes_ubx, descriptive_dict_ubx, zpdes_participants_ubx, \
    # baseline_participants_ubx = get_exp_status("v1_ubx")
    # zpdes_participants = zpdes_participants[7:9]
    # Sort per session + split into "all" and "only true" episodes
    # all_episodes_axa, true_episodes_axa = get_true_episodes(zpdes_participants_axa)
    # all_episodes_ubx, true_episodes_ubx, nb_per_blocks_ubx = get_true_episodes(zpdes_participants_ubx,
    #                                                                            nb_episodes=nb_episodes,
    #                                                                            keep_ntargets=None)
    # baseline_episodes_ubx, baseline_true_episodes_ubx, baseline_nb_per_blocks_ubx = get_true_episodes(
    #     baseline_participants_ubx, nb_episodes=nb_episodes, keep_ntargets=None)
    # all_episodes = {**all_episodes, **all_episodes_axa}
    # all_episodes = {**all_episodes, **all_episodes_ubx}
    # true_episodes = {**true_episodes, **true_episodes_axa}
    # true_episodes = {**true_episodes, **true_episodes_ubx}
    # mean_nb_of_episode_in_study(study, {**nb_per_blocks, **baseline_nb_per_blocks})
    # baseline_episodes_axa, baseline_true_episodes_axa = get_true_episodes(baseline_participants_axa)
    # baseline_episodes = {**baseline_episodes, **baseline_episodes_axa}
    # baseline_true_episodes = {**baseline_true_episodes, **baseline_true_episodes_axa}

    # #########################################################################################################@
    # (2) Frequency of proposed sub_parameters for each participant (radar plots):
    # #########################################################################################################@
    if get_frequency_radar_plots:
        return_dict, trajectory = get_params_total_frequency(all_episodes)
        return_dict_true, trajectory_true = get_params_total_frequency(true_episodes)
        plot_params_total_frequency(frequency_dict=return_dict, trajectory=trajectory, nb_per_block=nb_per_blocks,
                                    group='zpdes')
        plot_params_total_frequency(frequency_dict=return_dict_true, trajectory=trajectory_true,
                                    nb_per_block=nb_per_blocks_true, group='zpdes_true')
        return_dict_baseline, trajectory_baseline = get_params_total_frequency(baseline_episodes)
        return_dict_baseline_true, trajectory_baseline_true = get_params_total_frequency(baseline_true_episodes)
        plot_params_total_frequency(frequency_dict=return_dict_baseline, trajectory=trajectory_baseline,
                                    nb_per_block=baseline_nb_per_blocks, group='baseline')
        plot_params_total_frequency(frequency_dict=return_dict_baseline_true, trajectory=trajectory_baseline_true,
                                    nb_per_block=baseline_nb_per_blocks_true,
                                    group='baseline_true')
    # #########################################################################################################@
    # (4) Get entropies to summarize learning trajectories:
    # #########################################################################################################@
    if get_zpdes_entropy:
        entropy_zpdes = get_entropy(all_episodes)
        # entropy_zpdes_ubx = get_entropy(all_episodes_ubx)
        # display_sub_dims_entropy(entropy_zpdes, entropy_zpdes_ubx, nb_episodes)
        display_main_entropy(entropy_zpdes, entropy_zpdes_ref=None, nb_episodes=100)
    # #########################################################################################################
    # (5) Focus on the frequency per session of n_targets proposed / succeeded (histogram view)
    # ########################################################################################################
    if get_frequency_histograms:
        participants_all_frequency_ntargets = get_frequency_of_ntargets(all_episodes)
        participants_all_frequency_ntargets_baseline = get_frequency_of_ntargets(baseline_episodes)
        participants_true_frequency_ntargets = get_frequency_of_ntargets(true_episodes)
        participants_true_frequency_ntargets_baseline = get_frequency_of_ntargets(baseline_true_episodes)
        display_frequency_ntargets(participants_all_frequency_ntargets, nb_episodes=nb_episodes,
                                   participants_nb_per_block=nb_per_blocks, group="ZPDES")
        display_frequency_ntargets(participants_all_frequency_ntargets_baseline, nb_episodes=nb_episodes,
                                   participants_nb_per_block=baseline_nb_per_blocks, group="BASELINE")
    # #########################################################################################################
    # Focus on the mean activity for each nb_target per session (6 graph) @TODO: plot graph - doesnt work
    # Dict should look like participant: {nb_t_2: [[session_id, speed, radius, ...], [session_id, x,x,x]]}
    # participants_all_average_activity = get_average_activity(all_episodes)
    # participants_true_average_activity = get_average_activity(true_episodes)
    # display_average_activity(participants_true_average_activity)
    # #########################################################################################################

    # #########################################################################################################@
    # (6) Compute the mean success rate per session:
    # #########################################################################################################@
    if get_accuracy:
        # First the "binary" accuracy i.e nb_episodes_success / nb_episodes_tot
        participants_success_ps = get_mean_success_ps(all_episodes, true_episodes)
        participants_baseline_success_ps = get_mean_success_ps(baseline_episodes, baseline_true_episodes)
        # participants_success_ps_ubx = get_mean_success_ps(all_episodes_ubx, true_episodes_ubx)
        display_participants_success_ps(participants_success_ps=participants_success_ps,
                                        participant_success_ref=None, nb_episodes=nb_episodes)
        # participants_success_ps_ubx = get_mean_success_ps(baseline_episodes_ubx, baseline_true_episodes_ubx)
        display_participants_success_ps(participants_baseline_success_ps,
                                        participant_success_ref=None, condition='baseline',
                                        nb_episodes=nb_episodes)
        # Then - more interesting - the accuracy per episodes (i.e 3/4 targets)
        participants_success_continuous, participants_success_std = get_accuracy_per_episode(all_episodes)
        display_participants_success_ps(participants_success_ps=participants_success_continuous,
                                        participant_success_ref=None, nb_episodes=nb_episodes,
                                        success_type_title="continuous_F1_rate")
        display_participants_success_ps(participants_success_ps=participants_success_continuous,
                                        participant_success_ref=None, nb_episodes=nb_episodes,
                                        success_type_title="continuous_F1_rate_std",
                                        participant_std=participants_success_std)
        participants_baseline_success_continuous, participants_baseline_success_std = get_accuracy_per_episode(
            baseline_episodes)
        display_participants_success_ps(participants_success_ps=participants_baseline_success_continuous,
                                        participant_success_ref=None, nb_episodes=nb_episodes, condition='baseline',
                                        success_type_title="continuous_F1_rate")
        display_participants_success_ps(participants_success_ps=participants_baseline_success_continuous,
                                        participant_success_ref=None, nb_episodes=nb_episodes, condition='baseline',
                                        success_type_title="continuous_baseline_F1_rate_std",
                                        participant_std=participants_baseline_success_std)
        display_mean_zpdes_vs_baseline(participants_success_ps, participants_baseline_success_ps, title="Mean SR")
    # #########################################################################################################@
    # (7) Get some csv to get zpdes images (trajectory + internal states)
    # #########################################################################################################@
    if get_summary_trajectories:
        get_matrices(all_episodes)
        baseline_csv(baseline_episodes)
    # #########################################################################################################
    # (8) In order to see the evolution of exploration : get cumulative version of all_episodes / true_episodes
    # #########################################################################################################
    if get_novelty_trajectories or get_volume:
        cumu_true_episodes, len_cumu_true_episodes = get_cumulative_episode(true_episodes)
        cumu_all_episodes, len_cumu_all_episodes = get_cumulative_episode(all_episodes)
        cumu_true_episodes_baseline, len_cumu_true_episodes_baseline = get_cumulative_episode(baseline_true_episodes)
        cumu_all_episodes_baseline, len_cumu_all_episodes_baseline = get_cumulative_episode(baseline_episodes)
        # pickle.dump(cumu_true_episodes_zpdes, open('cumu_true_zpdes_32.pkl', 'wb'))
        # pickle.dump(cumu_all_episodes_zpdes, open('cumu_all_zpdes_32.pkl', 'wb'))
        # cumu_true_episodes_baseline = pickle.load(open('cumu_true_baseline_32.pkl', 'rb'))
        # cumu_all_episodes_baseline = pickle.load(open('cumu_all_baseline_32.pkl', 'rb'))
        # cumu_true_episodes_zpdes = pickle.load(open('cumu_true_zpdes_32.pkl', 'rb'))
        # cumu_all_episodes_zpdes = pickle.load(open('cumu_all_zpdes_32.pkl', 'rb'))
        # cumu_true_episodes_zpdes_ubx, len_cumu_true_episodes_zpdes_ubx = get_cumulative_episode(true_episodes_ubx)
        # cumu_all_episodes_zpdes_ubx, len_cumu_all_episodes_zpdes_ubx = get_cumulative_episode(all_episodes_ubx)
    # #########################################################################################################@
    # (3) Novelty (proba to sample an activity that has never been proposed):
    # #########################################################################################################@
    if get_novelty_trajectories:
        novelty_cumu_all_zpdes, novelty_cumu_true_zpdes = get_novelty(cumu_all_episodes), get_novelty(
            cumu_true_episodes)
        novelty_cumu_all_baseline, novelty_cumu_true_baseline = get_novelty(cumu_all_episodes_baseline), get_novelty(
            cumu_true_episodes_baseline)
        display_mean_zpdes_vs_baseline(novelty_cumu_all_zpdes, novelty_cumu_all_baseline, title='Novelty_all',
                                       nb_blocks=32)
        display_mean_zpdes_vs_baseline(novelty_cumu_true_zpdes, novelty_cumu_true_baseline, title='Novelty_true',
                                       nb_blocks=32)
    # #########################################################################################################@
    # (9) 4 dict to work on: all_episodes, true_episodes, cumu_all_episodes, cumu_true_episodes
    # #########################################################################################################@
    if get_volume:
        hull_volumes_all = get_participants_hypercube_per_session(all_episodes)
        hull_volumes_true = get_participants_hypercube_per_session(true_episodes)
        hull_volumes_all_baseline = get_participants_hypercube_per_session(baseline_episodes)
        hull_volumes_true_baseline = get_participants_hypercube_per_session(baseline_true_episodes)

        hull_volumes_cumu_true = get_participants_hypercube_per_session(cumu_true_episodes)
        hull_volumes_cumu_all = get_participants_hypercube_per_session(cumu_all_episodes)
        hull_volumes_cumu_true_baseline = get_participants_hypercube_per_session(cumu_true_episodes_baseline)
        hull_volumes_cumu_all_baseline = get_participants_hypercube_per_session(cumu_all_episodes_baseline)
        # hull_volumes_cumu_true_ubx = get_participants_hulls_per_session(cumu_true_episodes_zpdes_ubx)
        # hull_volumes_cumu_all_ubx = get_participants_hulls_per_session(cumu_all_episodes_zpdes_ubx)

        # Display volumes:
        # display_hulls(hull_volumes_all, title="All episode - hull per session - baseline", nb_blocks=8)
        # display_hulls(hull_volumes_true, title="True episode - hull per session - baseline", nb_blocks=8)
        display_volumes(hull_volumes_all_baseline, title="All episode - hypercube per session - baseline",
                        nb_episodes=nb_episodes, y_min=0, y_max=0.1)
        display_volumes(hull_volumes_true_baseline, title="True episode - hypercube per session - baseline",
                        nb_episodes=nb_episodes, y_min=0, y_max=0.1)
        display_volumes(hull_volumes_all, title="All episode - hypercube per session - zpdes",
                        nb_episodes=nb_episodes, y_min=0, y_max=0.1)
        display_volumes(hull_volumes_true, title="True episode - hypercube per session - zpdes",
                        nb_episodes=nb_episodes, y_min=0, y_max=0.1)

        display_volumes(hull_volumes_cumu_all, title="Cumu all episode - hypercube per session - zpdes",
                        nb_episodes=nb_episodes, y_min=0, y_max=0.3)
        display_volumes(hull_volumes_cumu_true, title="Cumu true episode - hypercube per session - zpdes",
                        nb_episodes=nb_episodes, y_min=0, y_max=0.3)
        display_volumes(hull_volumes_cumu_all_baseline, title="Cumu all episode - hypercube per session - baseline",
                        nb_episodes=nb_episodes, y_min=0, y_max=0.3)
        display_volumes(hull_volumes_cumu_true_baseline, title="Cumu true episode - hypercube per session - baseline",
                        nb_episodes=nb_episodes, y_min=0, y_max=0.3)
        # display_hulls(hull_volumes_cumu_true, participant_hull_ref=hull_volumes_cumu_true_ubx,
        #               title="True episode - cumulative hull - zpdes", nb_episodes=nb_episodes)
        # display_hulls(hull_volumes_cumu_all, participant_hull_ref=hull_volumes_cumu_all_ubx,
        #               title="All episode - cumulative hull - zpdes", nb_episodes=nb_episodes)
        # print(hull_volumes_all)
    # #########################################################################################################@
    # (10) Idle time:
    # #########################################################################################################@
    # idle_baseline = get_feature_from_sessions(baseline_episodes, feature_extractor=lambda x: x.idle_time/1000)
    # idle_zpdes = get_feature_from_sessions(all_episodes,  feature_extractor=lambda x: x.idle_time/1000)
    # display_mean_zpdes_vs_baseline(idle_zpdes, idle_baseline, title='idle_all', nb_blocks=32, fill_std=True)

    # #########################################################################################################@
    # (11) Nb episodes
    # #########################################################################################################@
    # nb_baseline = get_len_session(baseline_episodes, )
    # nb_zpdes = get_len_session(all_episodes)
    # display_mean_zpdes_vs_baseline(nb_zpdes, nb_baseline, title='nb_all', nb_blocks=8, fill_std=False)

    # #########################################################################################################@
    # (11) Create CSV for Individual differences analysis
    # #########################################################################################################@
    if create_ID_csv:
        # # Get age for each participant
        age_zpdes = pd.DataFrame.from_dict(
            map_keys(dict(map(lambda item: (item[0], get_age(item[0])), all_episodes.items()))),
            orient='index', columns=['age'])
        age_baseline = pd.DataFrame.from_dict(
            map_keys(dict(map(lambda item: (item[0], get_age(item[0])), baseline_episodes.items()))), orient='index',
            columns=['age'])
        # # Get adhd
        adhd_zpdes = pd.DataFrame.from_dict(
            map_keys(dict(map(lambda item: (item[0], get_attention_deficit(item[0])), all_episodes.items()))),
            orient='index', columns=['adhd'])
        adhd_baseline = pd.DataFrame.from_dict(
            map_keys(dict(map(lambda item: (item[0], get_attention_deficit(item[0])), baseline_episodes.items()))),
            orient='index',
            columns=['adhd'])
        # # Get nb years of study
        study_zpdes = pd.DataFrame.from_dict(
            map_keys(dict(map(lambda item: (item[0], get_study_duration(item[0])), all_episodes.items()))),
            orient='index',
            columns=['study_duration'])
        study_baseline = pd.DataFrame.from_dict(
            map_keys(dict(map(lambda item: (item[0], get_study_duration(item[0])), baseline_episodes.items()))),
            orient='index',
            columns=['study_duration'])
        # Before treating the results, parse all participant object to user_id
        all_episodes = {k.id: v for k, v in all_episodes.items()}
        baseline_episodes = {k.id: v for k, v in baseline_episodes.items()}
        # First idle_time
        idle_zpdes = pd.DataFrame.from_dict(
            get_feature_from_sessions(all_episodes, feature_extractor=lambda x: x.idle_time / 1000), orient='index',
            columns=['idle'])
        idle_baseline = pd.DataFrame.from_dict(
            get_feature_from_sessions(baseline_episodes, feature_extractor=lambda x: x.idle_time / 1000),
            orient='index', columns=['idle'])
        # # Get nb_episodes for each participant
        nb_zpdes = pd.DataFrame.from_dict(
            dict(map(lambda item: (item[0], get_nb_episodes(item[1])), all_episodes.items())), orient='index',
            columns=['nb_episodes'])
        nb_baseline = pd.DataFrame.from_dict(
            dict(map(lambda item: (item[0], get_nb_episodes(item[1])), baseline_episodes.items())), orient='index',
            columns=['nb_episodes'])
        # Get mean activity of first and last sessions
        parameters = ['n_targets', 'speed', 'tracking', 'probe', 'radius']
        act_session_first_zpdes = pd.DataFrame.from_dict(get_dict_mean_activity(all_episodes, session_id=0),
                                                         orient='index',
                                                         columns=[f'first_activity_{p}' for p in parameters])
        act_session_first_baseline = pd.DataFrame.from_dict(get_dict_mean_activity(baseline_episodes, session_id=0),
                                                            orient='index',
                                                            columns=[f'first_activity_{p}' for p in parameters])
        act_session_last_zpdes = pd.DataFrame.from_dict(get_dict_mean_activity(all_episodes, session_id=-1),
                                                        orient='index',
                                                        columns=[f'last_activity_{p}' for p in parameters])
        act_session_last_baseline = pd.DataFrame.from_dict(get_dict_mean_activity(baseline_episodes, session_id=-1),
                                                           orient='index',
                                                           columns=[f'last_activity_{p}' for p in parameters])
        # Merge everything into a single dataframe to export to csv
        df_zpdes = pd.concat(
            [idle_zpdes, nb_zpdes, age_zpdes, study_zpdes, act_session_first_zpdes, act_session_last_zpdes, adhd_zpdes], axis=1)
        df_baseline = pd.concat([idle_baseline, nb_baseline, age_baseline, study_baseline, act_session_first_baseline,
                                 act_session_last_baseline, adhd_baseline], axis=1)
        df_zpdes['condition'], df_baseline['condition'] = 'zpdes', 'baseline'
        df = pd.concat([df_zpdes, df_baseline])
        df.to_csv(f"feature_csv_{study}.csv")

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# For now, just use one participant as an example:
print(os.getcwd())
df = pd.read_csv('mot_app/analysis_extraction/outputs/prolific/zpdes_states.csv')
df = pd.read_csv('zpdes_states_exploration.csv')
# df_baseline = pd.read_csv('../outputs/baseline_states.csv')
df = df.drop(columns=['Unnamed: 0'])
columns = ['speed_values', 'tracking_duration_values', 'probe_duration_values', 'radius_values']
for col in columns:
    df[col] = df[col].apply(lambda elt: [float(value) for value in elt[1:-1].split(',')])
path = './static/images/zpdes_app/'


def create_path(participant, path):
    participant = path + participant
    if not os.path.isdir(participant):
        os.mkdir(participant)
    if not os.path.isdir(participant + '/main_distrib'):
        os.mkdir(participant + '/main_distrib')
    if not os.path.isdir(participant + '/radar_subs'):
        os.mkdir(participant + '/radar_subs')
    if not os.path.isdir(participant + '/trajectory'):
        os.mkdir(participant + '/trajectory')
        os.mkdir(participant + '/trajectory/results')
        os.mkdir(participant + '/trajectory/main')


for participant in list(df.participant.unique()):
    create_path(participant, path + 'zpdes/')


# for participant in list(df_baseline.participant.unique()):
#     create_path(participant, path + '/baseline/')


def plot_histogram(participant, index_episode, df_participant_episode):
    participant = path + 'zpdes/' + participant
    support_main = [i for i in range(6)]
    main_values = df_participant_episode['main_value'].values
    main_success = df_participant_episode['main_success'].values
    plt.tight_layout(pad=3.0)
    # plt.title(f'Main dimension, episode={index_episode}, LP values') # old title
    plt.title(f'Main dimension, episode={index_episode}, \n [Bandit_val=0.2*old_alp + 0.8*reward] values')
    plt.bar(support_main, main_values)
    plt.ylim((0, 0.5))
    plt.savefig(os.path.join(participant, 'main_distrib', f"bandits_{index_episode}.png"))
    plt.close()
    plt.tight_layout(pad=3.0)
    # plt.title(f'Main dimension, episode={index_episode}, ALP') # old title
    plt.title(f'Main dimension, episode={index_episode}, [Reward] values')
    plt.ylim((0, 0.5))
    plt.bar(support_main, main_success)
    plt.savefig(os.path.join(participant, 'main_distrib', f"success_{index_episode}.png"))
    plt.close()


def plot_baseline_histogram(participant, index_episode, df_participant_episode):
    participant = path + '/baseline/' + participant
    support_main = [i for i in range(6)]
    main_index = df_participant_episode['main_index'].values[0]
    main_values = [0 if idx != main_index else 1 for idx in range(6)]
    plt.tight_layout(pad=3.0)
    plt.title(f'Main dimension, episode={index_episode}')
    plt.bar(support_main, main_values)
    plt.savefig(os.path.join(participant, 'main_distrib', f"bandits_{index_episode}.png"))
    plt.close()


def plot_radar(participant, df_participant_episode):
    label_loc = np.linspace(start=0, stop=360, num=5)
    main_sample = int(df_participant_episode.iloc[0]['episode_sample'][10])
    sub_sample = list(map(lambda elt: int(elt), (df_participant_episode.iloc[0]['episode_sample'][22:-2]).split(',')))
    color_sample = 'g' if df_participant_episode.iloc[0]['results'] == 1 else 'red'
    # label_loc = np.append(label_loc, [0])
    plot_sub_dim_radar(participant, df_participant_episode, label_loc, main_sample, sub_sample, color_sample)
    # plot_radar_HD_values(df_participant_episode, label_loc, main_sample, sub_sample)


def get_active(list_values):
    """ returns: (min_index, max_index)"""
    max_index = np.where(np.array(list_values[0]) > 0)
    return max_index[0][-1]


def get_max(list_values):
    max_index = np.where(np.array(list_values[0]) == np.amax(np.array(list_values[0])))
    return max_index[0][-1]


def plot_sub_dim_radar(participant, df_participant_episode, label_loc, main_sample, sub_sample, color_sample):
    fig, axs = plt.subplots(2, 3, subplot_kw={'projection': 'polar'}, figsize=(15, 15))
    fig.tight_layout(pad=8.0)
    for idx, ax in enumerate(axs.flat):
        sub_dim = df_participant_episode.query(f'main_index == {idx}')
        ax.set_title(f'Dim {idx}, LP: {sub_dim["main_value"].values[0]:.3f}')
        ax.set_thetagrids(angles=label_loc, labels=['speed', 'tracking', 'probe', 'radius', 'speed'])
        ax.set_rgrids(range(0, 8), labels='')
        if (sub_dim['main_value'].values[0] == 0):
            ax.set_facecolor('black')
        else:
            speed_max = get_active(sub_dim['speed_values'].values)
            radius_max = get_active(sub_dim['radius_values'].values)
            tracking_max = get_active(sub_dim['tracking_duration_values'].values)
            probe_max = get_active(sub_dim['probe_duration_values'].values)
            speed_high_prob_max = get_max(sub_dim['speed_values'].values)
            radius_high_prob_max = get_max(sub_dim['radius_values'].values)
            tracking_high_prob_max = get_max(sub_dim['tracking_duration_values'].values)
            probe_high_prob_max = get_max(sub_dim['probe_duration_values'].values)
            activity_max = [speed_max, tracking_max, probe_max, radius_max, speed_max]
            # ax.set_thetagrids(angles=label_loc, labels=get_label_array(sub_dim, activity_max))
            activity_high_prob_max = [speed_high_prob_max, tracking_high_prob_max, probe_high_prob_max,
                                      radius_high_prob_max, speed_high_prob_max]
            ax.scatter(np.deg2rad(label_loc), activity_high_prob_max, color='grey', linewidth=0.5)
            ax.plot(np.deg2rad(label_loc), activity_max, color='blue', linewidth=0.5)
            ax.fill(np.deg2rad(label_loc), activity_max, color='blue', alpha=0.1)
            if idx == main_sample:
                ax.plot(np.deg2rad(label_loc), sub_sample + [sub_sample[0]], c=color_sample)
                ax.scatter(np.deg2rad(label_loc), sub_sample + [sub_sample[0]], c=color_sample)
            ax.set_rgrids(range(0, 8), labels=[''] + [f'{i}' for i in range(1, 8)])
    participant = path + '/zpdes/' + participant
    fig.savefig(os.path.join(participant, 'radar_subs', f"{index_episode}.png"))
    plt.close(fig)


def get_label_array(values, max):
    # speed_label = f"speed - SR: {np.mean(list(map(lambda x: float(x), values['speed_success'].values[0].strip('][').split(',')))):2.1f} %"
    speed_label = f"speed - SR: {get_SR_from_success(reformat_success_array(values['speed_success'].values[0]), max[0]):2.3f} %"
    tracking_label = f"tracking - SR: {get_SR_from_success(reformat_success_array(values['tracking_duration_success'].values[0]), max[1]):2.3f} %"
    probe_label = f"probe - SR: {get_SR_from_success(reformat_success_array(values['probe_duration_success'].values[0]), max[2]):2.3f} %"
    radius_label = f"radius - SR: {get_SR_from_success(reformat_success_array(values['radius_success'].values[0]), max[3]):2.3f} %"
    return [speed_label, tracking_label, probe_label, radius_label, speed_label]


def reformat_success_array(string_list):
    return string_list.strip('][').split(',')


def get_SR_from_success(list_success, max_index):
    list_success = list(map(lambda x: float(x), list_success))
    list_success = list_success[:max_index+1]
    # list_success = list(filter(lambda num: num != 0, list_success))
    if len(list_success) == 0:
        return 0
    return np.mean(list_success)


def plot_baseline_radar(participant, df_participant_episode):
    label_loc = np.linspace(start=0, stop=360, num=5)
    main_sample = int(df_participant_episode.iloc[0]['episode_sample'][10])
    sub_sample = list(map(lambda elt: int(elt), (df_participant_episode.iloc[0]['episode_sample'][22:-2]).split(',')))
    color_sample = 'g' if df_participant_episode.iloc[0]['results'] == 1 else 'red'
    baseline_plot_sub_dim_radar(participant, label_loc, main_sample, sub_sample, color_sample)


def baseline_plot_sub_dim_radar(participant, label_loc, main_sample, sub_sample, color_sample):
    fig, axs = plt.subplots(2, 3, subplot_kw={'projection': 'polar'}, figsize=(15, 15))
    fig.tight_layout(pad=3.0)
    for idx, ax in enumerate(axs.flat):
        ax.set_thetagrids(angles=label_loc, labels=['speed', 'tracking', 'probe', 'radius', 'speed'])
        ax.set_rgrids(range(0, 8), labels='')
        ax.set_title(f'Dim {idx}')
        if idx != main_sample:
            ax.set_facecolor('black')
        else:
            ax.plot(np.deg2rad(label_loc), sub_sample + [sub_sample[0]], c=color_sample)
            ax.scatter(np.deg2rad(label_loc), sub_sample + [sub_sample[0]], c=color_sample)
            ax.set_rgrids(range(0, 8), labels=[''] + [f'{i}' for i in range(1, 8)])
    participant = path + '/baseline/' + participant
    fig.savefig(os.path.join(participant, 'radar_subs', f"{index_episode}.png"))
    plt.close(fig)


def mean(list):
    return np.array(list).mean()


def std(list):
    return np.array(list).std()


def get_progression_till_index_episode(participant, index_episode, df_participant, window_size):
    # if tmp_episode_index < window_size:
    window_episode_results = []
    window_episode_main = []
    trajectory_main_mean = []
    trajectory_main_std = []
    trajectory_results_mean = []
    trajectory_results_std = []
    for tmp_episode_index in range(index_episode):
        if len(window_episode_main) > window_size:
            trajectory_main_mean.append(mean(window_episode_main))
            trajectory_main_std.append(std(window_episode_main))
            trajectory_results_mean.append(mean(window_episode_results))
            trajectory_results_std.append(std(window_episode_results))
            window_episode_main.pop(0)
            window_episode_results.pop(0)
        tmp_episode = df_participant.query(f'episode == {tmp_episode_index}')
        if len(tmp_episode) > 0:
            window_episode_results.append(tmp_episode.iloc[0]['results'])
            window_episode_main.append(int(tmp_episode.iloc[0]['episode_sample'][10]))
    support = np.linspace(0, len(trajectory_results_mean), len(trajectory_results_mean))
    trajectory_results_mean = np.array(trajectory_results_mean)
    trajectory_results_std = np.array(trajectory_results_std)
    trajectory_main_mean = np.array(trajectory_main_mean)
    trajectory_main_std = np.array(trajectory_main_std)
    plt.title(f"Results - window: {window_size} - end episode index {index_episode}")
    plt.plot(support, trajectory_results_mean, color='blue', label="results")
    # plt.scatter(support, trajectory_results_mean, color='blue')
    plt.fill_between(support, trajectory_results_mean + trajectory_results_std,
                     trajectory_results_mean - trajectory_results_std, facecolor='blue', alpha=0.1)
    plt.savefig(os.path.join(participant, 'trajectory', 'results', f"{index_episode}-{window_size}.png"))
    plt.close()
    plt.figure()
    plt.title(f"Main trajectory - window: {window_size} - end episode index {index_episode}")
    plt.plot(support, trajectory_main_mean, label="trajectory", color='red')
    # plt.scatter(support, trajectory_main_mean, color='red')
    plt.fill_between(support, trajectory_main_mean + trajectory_main_std,
                     trajectory_main_mean - trajectory_main_std, alpha=0.4, facecolor='red')
    plt.savefig(os.path.join(participant, 'trajectory', 'main', f"{index_episode}.png"))
    plt.close()


def run_all(index_episode, df_participant):
    df_participant_episode = df_participant.query(f'episode == {index_episode}')
    if len(df_participant_episode) > 0:
        plot_histogram(participant, index_episode, df_participant_episode)
        # plot_radar(participant=participant, df_participant_episode=df_participant_episode)
        # get_progression_till_index_episode(participant, index_episode, df_participant, 10)


def run_all_baseline(index_episode, df_participant):
    df_participant_episode = df_participant.query(f'episode == {index_episode}')
    if len(df_participant_episode) > 0:
        plot_baseline_histogram(participant, index_episode, df_participant_episode)
        plot_baseline_radar(participant=participant, df_participant_episode=df_participant_episode)


def clean_episodes_nb(groupby_df):
    if len(groupby_df) > 6:
        groupby_df.episode.iloc[6:] = groupby_df.episode.iloc[6:] + 1
    return groupby_df


if __name__ == '__main__':
    # df = df[df['participant'] == 'mangdoline']
    participant_list = ['nolan', 'kelly.vin']
    # for participant in list(df.participant.unique()):
    for participant in participant_list:
        print(participant)
        df_participant = df[df['participant'] == participant]
        df_participant = df_participant.groupby('episode').apply(clean_episodes_nb)
        nb_episode = df_participant['episode'].max()
        for index_episode in range(nb_episode):
            run_all(index_episode, df_participant)
            if index_episode % 100 == 0:
                print(index_episode)

    # for participant in list(df_baseline.participant.unique()):
    #     print(participant)
    #     df_participant = df_baseline[df_baseline['participant'] == participant]
    #     df_participant = df_participant.groupby('episode').apply(clean_episodes_nb)
    #     nb_episode = df_participant['episode'].max()
    #     for index_episode in range(nb_episode):
    #         run_all_baseline(index_episode, df_participant)
    #         if index_episode % 100 == 0:
    #             print(index_episode)

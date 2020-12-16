# @TODO: step of "activations" --> zpdes thesis (get steps)
# @TODO: get values at each steps in wrapper
# @TODO: gather everything in report
# @TODO: try to find where algorithm breaks

from mot_results.get_bandits.wrapper import MotWrapperResults
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import kidlearn_lib as k_lib
from kidlearn_lib import functions as func
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
import json


def bandit_values_to_csv(path='get_bandits/data/episodes/laetitia.csv', output='laetitia_bandits.json'):
    """
    Use participant's history to create a json file with bandit values
    """
    history = pd.read_csv(path)
    history['episode_number'].apply(pd.to_numeric)
    history = history.sort_values('episode_number', axis=0).reset_index(drop=True)
    dir_path = "../mot_project/interface_app/static/JSON/config_files"
    zpdes_params = func.load_json(file_name='ZPDES_mot', dir_path=dir_path)
    seq_manager = k_lib.seq_manager.ZpdesHssbg(zpdes_params)
    mot_wrapper = MotWrapperResults()
    for index, episode in history.iterrows():
        seq_manager = mot_wrapper.update(episode, seq_manager)
    with open(output, 'w') as outfile:
        json.dump(mot_wrapper.bandit_values, outfile)


def plot_states(data, nb_row, nb_col, fig_title, save=True, save_name='', show=True):
    """
    Take a dict and plot the graph of states evolution through time
    """
    labels = ["nb2", "nb3", "nb4", "nb5", "nb6", "nb7"]
    main = np.array(data['MAIN']['nb'])
    print(main.shape)
    time = np.linspace(1, main.shape[0], main.shape[0])
    fig, axs = plt.subplots(nb_row, nb_col)
    fig.suptitle(fig_title)
    for idx, ax in enumerate(axs.flat):
        ax.plot(time, main[:, idx])
        ax.set_xlabel(labels[idx])
    # plt.scatter(states, time)
    if save:
        fig.savefig('get_bandits/data/results/'+save_name)
    if show:
        plt.show()



def plot_states_sub_dim():
    pass


if __name__ == '__main__':
    bandit_values_to_csv()
    with open('get_bandits/data/bandits/laetitia_bandits.json') as json_file:
        data = json.load(json_file)
    plot_states(data, nb_row=3, nb_col=2, fig_title='Laetitia pre-activation', save_name='laetitia_results')
    # print(pd.DataFrame(data['MAIN']))
    # print((data['nb2'][0]))


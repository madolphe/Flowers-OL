import numpy as np
import math
import pandas as pd
import json
import kidlearn_lib as k_lib
from kidlearn_lib import functions as func
import copy

class MotWrapperResults:
    """
        Wrapper class for kidlearn algorithms to produce correct parameterized tasks dict
    """

    def __init__(self, admin_pannel=False, game_time=30 * 60):
        # Just init "fixed parameters":
        self.parameters = {'angle_max': 9, 'angle_min': 3, 'radius': 40, 'speed_min': 4, 'speed_max': 4,
                           'episode_number': 0, 'nb_target_retrieved': 0,
                           'nb_distract_retrieved': 0, 'id_session': 0, 'presentation_time': 1, 'fixation_time': 1,
                           'debug': 0, 'secondary_task': 'none', 'SRI_max': 2, 'RSI': 1, 'delta_orientation': 45,
                           'gaming': 1, 'game_time': game_time, 'admin_pannel': admin_pannel, 'score': 0}
        # Could be obtained through reading graph (to be automated!):
        self.values = {'n_targets': np.array([2, 3, 4, 5, 6, 7], dtype=float),
                       'speed_max': np.linspace(2, 7, 11, dtype=float),
                       'tracking_time': np.linspace(3, 7, 9, dtype=float),
                       'probe_time': np.linspace(4, 2, 11, dtype=float),
                       'n_distractors': np.linspace(1, 4, 4, dtype=float)}
        self.lvls = ["nb2", "nb3", "nb4", "nb5", "nb6", "nb7"]
        self.values_index = ['speed_max', 'tracking_time', 'probe_time', 'n_distractors']
        self.bandit_values = {'MAIN': {'nb': []},
                              'nb2': {'speed_max': [], 'tracking_time': [], 'probe_time': [], 'n_distractors': []},
                              'nb3': {'speed_max': [], 'tracking_time': [], 'probe_time': [], 'n_distractors': []},
                              'nb4': {'speed_max': [], 'tracking_time': [], 'probe_time': [], 'n_distractors': []},
                              'nb5': {'speed_max': [], 'tracking_time': [], 'probe_time': [], 'n_distractors': []},
                              'nb6': {'speed_max': [], 'tracking_time': [], 'probe_time': [], 'n_distractors': []},
                              'nb7': {'speed_max': [], 'tracking_time': [], 'probe_time': [], 'n_distractors': []}
                              }

    def sample_task(self, seq):
        """
        Method that convert a node in ZPD graph to real value for MOT
        :return:
        """
        act = seq.sample()
        parameters = {
            'n_targets': self.values['n_targets'][act['MAIN'][0]],
            'speed_max': self.values['speed_max'][act[self.lvls[act['MAIN'][0]]][0]],
            'speed_min': self.values['speed_max'][act[self.lvls[act['MAIN'][0]]][0]],
            'tracking_time': self.values['tracking_time'][act[self.lvls[act['MAIN'][0]]][1]],
            'probe_time': self.values['probe_time'][act[self.lvls[act['MAIN'][0]]][2]],
            'n_distractors': self.values['n_distractors'][act[self.lvls[act['MAIN'][0]]][3]]}
        for key, value in parameters.items():
            self.parameters[key] = value
        try:
            self.parameters['n_distractors'] += self.parameters['n_targets']
        except KeyError:
            print('No key')
        return self.parameters

    def update(self, episode, seq):
        """
        Given one episode update and return the seq manager.
        Also store last episode results (i.e ep_number, nb_targets_retrieved, nb distract_retrieved)
        :param episode:
        :param seq:
        :return:
        """
        print("Numéro de l'episode: {}, values in csv: "
              "speed:{} | "
              "n_targets: {} | "
              "n_disctract: {} | "
              "probe_time: {} | "
              "tracking_time: {} | ".format(episode['episode_number'], episode["speed_max"],
                                         episode["n_targets"], episode["n_distractors"], float(episode["probe_time"]),
                                         episode["tracking_time"]))
        parsed_episode = self.parse_activity(episode)
        seq.update(parsed_episode['act'], parsed_episode['ans'])
        self.get_bandit_values(seq)
        print("Numéro de l'episode: {} \n Parsed values: {} \n" 
              "---------------------".format(episode['episode_number'], parsed_episode))
        # Store in mot_wrapper result of last episode (useful for sampling new task)
        self.parameters['nb_target_retrieved'] = episode['nb_target_retrieved']
        self.parameters['nb_distract_retrieved'] = episode['n_distractors']
        # Count how many episodes were played for this init of MOT-wrapper e.g for a session
        self.parameters['episode_number'] += 1
        return seq

    def get_bandit_values(self, seq):
        band_val = copy.deepcopy(seq.get_state()['bandval'])
        # print("BANDIT VALUES:")
        for key in band_val.keys():
            if key not in band_val:
                print("NOT IN BAND VAL", key)
            else:
                if key == 'MAIN':
                    self.bandit_values[key]['nb'].append(band_val['MAIN'][0])
                else:
                    for index, sub_dim in enumerate(self.values_index):
                        self.bandit_values[key][sub_dim].append(band_val[key][index])
                # print(self.bandit_values[key])
        # print("MAIN BANDIT VALUE:", self.bandit_values['MAIN'])

    @staticmethod
    def get_results(episode):
        """
        Take a line of a pandas dataframe episode and return the result i.e True if nb_target == nb_target_retrieved
        and nb_distract == nb_target_retrieved
        """
        # print("RESULTATS:")
        # print("Nb target: {}, retrieved: {}".format(episode['nb_target_retrieved'], episode['n_targets']))
        # print("Nb distract: {}, retrieved: {}".format(episode['nb_distract_retrieved'], episode['n_distractors']))
        if (episode['nb_target_retrieved'] == episode['n_targets']) and \
                episode['nb_distract_retrieved'] == episode['n_distractors']:
            return 1
        else:
            return 0

    def parse_activity(self, episode):
        # First check if this act was successful:
        # print("GRID: {}".format(self.values))
        answer = self.get_results(episode)
        # Adjust values in 'n_distractors':
        n_d_values = np.array([self.values['n_distractors'][i] + float(episode['n_targets'])
                               for i in range(len(self.values['n_distractors']))])
        # Then just parse act to ZPDES formalism:
        speed_i = np.where(self.values['speed_max'] == float(episode['speed_max']))[0][0]
        n_targets_i = np.where(self.values['n_targets'] == float(episode['n_targets']))[0][0]
        n_distractors_i = np.where(n_d_values == float(episode['n_distractors']))[0][0]
        track_i = np.where(self.values['tracking_time'] == float(episode['tracking_time']))[0][0]
        # print("COMPARAISON QUI TUE:", self.values['probe_time'] == float(episode['probe_time']),
        # episode['probe_time'])
        # print("AVEC BUILT-IN FUNC:", [math.isclose(elt, float(episode['probe_time']))
        # for elt in self.values["probe_time"]])
        probe_i = np.where([math.isclose(elt, float(episode['probe_time'])) for elt in self.values["probe_time"]])[0][0]
        # episode_parse = {'MAIN': [n_targets_i], str(self.lvls[n_targets_i]): [speed_i, n_distractors_i, track_i,
        # probe_i]}
        episode_parse = {'MAIN': [n_targets_i],
                         str(self.lvls[n_targets_i]): [speed_i, track_i, probe_i, n_distractors_i]}
        # print("Seq manager sampled task with {} targets, {} distractors with speed {}, "
        #      "tracking time {} and probe_time {}".format(n_targets_i, n_distractors_i, speed_i, track_i, probe_i))
        return {'act': episode_parse, 'ans': answer}

    def set_parameter(self, name, new_value):
        """ Update parameter value. If the value doesn't exist, it automatically creates on.
        Otherwise write new value.
        :param name: string
        :param new_value: new object to add
        """
        # print("UPDATE {} parameter, with new val {}".format(name, str(new_value)))
        self.parameters[name] = new_value


def bandit_values_to_csv(path='get_bandits/laetitia_all.csv', output='laetitia_values.json'):
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
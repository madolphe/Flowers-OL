import kidlearn_lib as k_lib
from kidlearn_lib import functions as func
import numpy as np


class SeqManager:
    """
        Wrapper class for kidlearn algorithms to produce correct parameterized tasks dict
    """
    def __init__(self, condition, history, file_name="ZPDES_mot", dir_path="interface_app/static/JSON/config_files"):

        if condition == 'zpdes':
            zpdes_params = func.load_json(file_name=file_name, dir_path=dir_path)
            self.seq = k_lib.seq_manager.ZpdesHssbg(zpdes_params)
        else:
            mot_baseline_params = func.load_json(file_name="mot_baseline_params", dir_path="config_files")
            self.seq = k_lib.seq_manager.MotBaselineSequence(mot_baseline_params)
        self.update(history)
        # Could be obtained through reading graph (to be automated!):
        self.values = { 'n_dots': np.array([2, 3, 4, 5, 6, 7], dtype=float),
                        'speed': np.linspace(2, 7, 11, dtype=float),
                        'tracking_duration': np.linspace(3, 7, 9, dtype=float),
                        'probe_duration': np.linspace(3, 1, 11, dtype=float),
                        'total_number': np.linspace(1, 4, 4, dtype=float)}
        self.lvls = ["nb2", "nb3", "nb4", "nb5", "nb6", "nb7"]

    def sample_task(self):
        """
        Method that convert a node in ZPD graph to real value for MOT
        :return:
        """
        act = self.seq.sample()
        parameters = {
                        'n_dots': self.values['n_dots'][act['MAIN'][0]],
                        'speed': self.values['speed'][act[self.lvls[act['MAIN'][0]]][0]],
                        'tracking_duration': self.values['tracking_duration'][act[self.lvls[act['MAIN'][0]]][1]],
                        'probe_duration': self.values['probe_duration'][act[self.lvls[act['MAIN'][0]]][2]],
                        'total_number': self.values['total_number'][act[self.lvls[act['MAIN'][0]]][3]]
        }
        return parameters

    def update(self, history):
        for episode in history:
            self.seq.update(self.parse_activity(episode))

    def parse_activity(self, episode):
        # First check if this act was successful:
        answer = 0
        if episode.nb_target_retrieved == episode.n_targets:
            if episode.nb_distract_retrieved == episode.n_distractors:
                answer = 1
        # Then just parse act to ZPDES formalism:
        speed_i = np.where(self.values['n_dots'] == episode.speed_max)
        n_dots_i = np.where(self.values['n_dots'] == episode.n_targets)
        n_dist_i = np.where(self.values['n_dots'] == episode.n_distractors)
        track_i = np.where(self.values['n_dots'] == episode.tracking_time)
        episode = {'MAIN': [n_dist_i], str(self.lvl[n_dots_i]): [speed_i, n_dist_i, track_i, 0]}
        return {'act': episode, 'ans': answer}

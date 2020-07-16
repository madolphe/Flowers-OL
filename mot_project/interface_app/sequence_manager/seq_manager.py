import numpy as np
from ..models import Answer


class MotParamsWrapper:
    """
        Wrapper class for kidlearn algorithms to produce correct parameterized tasks dict
    """
    def __init__(self, participant, admin_pannel=False):
        self.participant = participant
        screen_params = Answer.objects.get(participant=participant, question__handle='prof-1').value
        # Just init "fixed parameters":
        self.parameters = {'angle_max': 9, 'angle_min': 3, 'radius': 90, 'speed_min': 4, 'speed_max': 4,
                           'screen_params': float(screen_params), 'episode_number': 0, 'nb_target_retrieved': 0,
                           'nb_distract_retrieved': 0, 'id_session': 0, 'presentation_time': 1, 'fixation_time': 1,
                           'debug': 0, 'secondary_task': 'none', 'SRI_max': 2, 'RSI': 1, 'delta_orientation': 45,
                           'gaming': 1, }
        # Could be obtained through reading graph (to be automated!):
        self.values = {'n_targets': np.array([2, 3, 4, 5, 6, 7], dtype=float),
                       'speed_max': np.linspace(2, 7, 11, dtype=float),
                       'tracking_time': np.linspace(3, 7, 9, dtype=float),
                       'probe_time': np.linspace(3, 1, 11, dtype=float),
                       'n_distractors': np.linspace(1, 4, 4, dtype=float)}
        print(self.values)
        self.lvls = ["nb2", "nb3", "nb4", "nb5", "nb6", "nb7"]

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
        return self.parameters

    def update(self, episode, seq):
        """
        Given one episode update and return the seq manager.
        Also store last episode results (i.e ep_number, nb_targets_retrieved, nb distract_retrieved)
        :param episode:
        :param seq:
        :return:
        """
        parsed_episode = self.parse_activity(episode)
        seq.update(parsed_episode['act'], parsed_episode['ans'])
        # Store in mot_wrapper result of last episode (useful for sampling new task)
        self.parameters['nb_target_retrieved'] = episode.nb_target_retrieved
        self.parameters['nb_distract_retrieved'] = episode.n_distractors
        return seq

    def parse_activity(self, episode):
        # First check if this act was successful:
        answer = episode.get_results
        print("Update answer equals:", answer)
        # Then just parse act to ZPDES formalism:
        speed_i = np.where(self.values['speed_max'] == float(episode.speed_max))[0][0]
        n_targets_i = np.where(self.values['n_targets'] == float(episode.n_targets))[0][0]
        n_distractors_i = np.where(self.values['n_distractors'] == float(episode.n_distractors))[0][0]
        track_i = np.where(self.values['tracking_time'] == float(episode.tracking_time))[0][0]
        probe_i = np.where(self.values['probe_time'] == float(episode.probe_time))[0][0]
        episode_parse = {'MAIN': [n_targets_i], str(self.lvls[n_targets_i]): [speed_i, n_distractors_i, track_i, probe_i]}
        print("Seq manager sampled task with {} targets, {} distractors with speed {}, "
              "tracking time {} and probe_time {}".format(n_targets_i, n_distractors_i, speed_i, track_i, probe_i))
        return {'act': episode_parse, 'ans': answer}

    def set_parameter(self, name, new_value):
        """ Update parameter value. If the value doesn't exist, it automatically creates on.
        Otherwise write new value.
        :param name: string
        :param new_value: new object to add
        """
        self.parameters[name] = new_value
        return self.parameters

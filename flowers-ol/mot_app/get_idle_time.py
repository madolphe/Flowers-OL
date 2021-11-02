import importlib
import os
import django

# Connection to flowers-DB:
flowers_ol = importlib.import_module("flowers-ol.settings")

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "flowers-ol.settings"
)
django.setup()

from mot_app.models import Episode


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
                idle_times[session_key].append((delta.total_seconds()-episode_length))
        print(sum(idle_times[session_key])/len(idle_times[session_key]))


def check_episode_date():
    pass


if __name__ == '__main__':
    get_mean_idle_time("v1_ubx")

from django.urls import path, re_path
from . import views

urlpatterns = [
    # ZPDES urls
    path('app_MOT', views.MOT_task, name='app_MOT'),
    path('next_episode', views.next_episode, name='next_episode'),
    path('restart_episode', views.restart_episode, name='restart_episode'),
    path('set_mot_params', views.set_mot_params, name='set_mot_params'),
    path('display_progression', views.display_progression, name="display_progression"),
    path('mot_close_task', views.mot_close_task, name='mot_close_task'),
    path('enumeration_task', views.enumeration_task, name='enumeration_task'),
]
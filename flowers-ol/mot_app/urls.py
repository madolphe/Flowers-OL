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
    path('cognitive_assessment_home', views.cognitive_assessment_home, name='cognitive_assessment_home'),
    path('cognitive_task', views.cognitive_task, name='cognitive_task'),
    path('exit_view_cognitive_task', views.exit_view_cognitive_task, name='exit_view_cognitive_task'),
    path('tutorial/<str:task_name>', views.tutorial, name="tutorial"),
    path('mot_consent_page', views.mot_consent_page, name="mot_consent_page"),
    path('general_tutorial', views.general_tutorial, name="general_tutorial"),
    path('completion_code', views.completion_code, name="completion_code"),
    path('dashboard', views.dashboard, name="dashboard")
]
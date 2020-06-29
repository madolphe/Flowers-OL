from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.login_page, name='login_page'),
    re_path(r'^study=(.*)$', views.login_page, name='login_page'), # Still not sure how this works, but it prevents the login page warning if user logs out from interface
    path('home', views.home, name='home'),
    path('user_logout', views.user_logout, name='user_logout'),
    path('signup_page', views.signup_page, name='signup_page'),
    path('consent_page', views.consent_page, name='consent_page'),
    path('start_task', views.start_task, name='start_task'),
    path('end_task', views.end_task, name='end_task'),

    # ZPDES urls
    path('get_profil', views.get_profil, name='profil'),
    path('get_attention', views.get_attention, name='attention'),
    path('app_2D', views.visual_2d_task, name='app_2D'),
    path('app_3D', views.visual_3d_task, name='app_3D'),
    path('app_MOT', views.MOT_task, name='app_MOT'),
    path('next_episode', views.next_episode, name='next_episode'),
    path('restart_episode', views.restart_episode, name='restart_episode'),

    ## JOLD urls
    path('JOLD/StartPracticeBlockLL', views.joldStartPracticeBlockLL, name='JOLD_start_practice_block_ll'),
    path('JOLD/SaveTrialLL', views.joldSaveTrialLL, name='JOLD_save_trial_LL'),
    path('JOLD/ClosePracticeBlock', views.joldClosePracticeBlock, name='JOLD_close_practice_block'),
    path('JOLD/QuestionBlock/', views.joldQuestionBlock, name='JOLD_question_block'),
    path('JOLD/EndOfSession', views.joldEndOfSession, name='JOLD_end_of_session'),
    path('JOLD/EndOfSession/<int:choice>/', views.joldEndOfSession, name='JOLD_end_of_session'),
    path('JOLD/Thanks', views.joldThanks, name='JOLD_thanks')
]

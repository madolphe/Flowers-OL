from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    re_path(r'^study=(.*)$', views.home, name='home'), # Still not sure how this works, but it prevents the login page warning if user logs out from interface
    path('home_user', views.home_user, name='home_user'),
    path('user_logout', views.user_logout, name='user_logout'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('consent_page', views.consent_page, name='consent_page'),
    path('off_session', views.off_session, name='off_session'),
    path('app_2D', views.visual_2d_task, name='app_2D'),
    path('app_3D', views.visual_3d_task, name='app_3D'),
    path('app_MOT', views.MOT_task, name='app_MOT'),
    path('next_episode', views.next_episode, name='next_episode'),
    path('restart_episode', views.restart_episode, name='restart_episode'),

    ## JOLD urls
    path('JOLD/home_user', views.home_user, name='home_user'),
    path('JOLD/StartPracticeBlockLL', views.joldStartPracticeBlockLL, name='JOLD_start_practice_block_ll'),
    path('JOLD/StartPracticeBlockLL/<int:forced>/', views.joldStartPracticeBlockLL, name='JOLD_start_practice_block_ll'),
    path('JOLD/SaveTrialLL', views.joldSaveTrialLL, name='JOLD_save_trial_LL'),
    path('JOLD/ClosePracticeBlock', views.joldClosePracticeBlock, name='JOLD_close_practice_block'),
    path('JOLD/Transition', views.joldTransition, name='JOLD_transition'),
    path('JOLD/QuestionBlock/', views.joldQuestionBlock, name='JOLD_question_block'),
    path('JOLD/QuestionBlock/<int:num>/', views.joldQuestionBlock, name='JOLD_question_block'),
    path('JOLD/EndOfSession', views.joldEndOfSession, name='JOLD_end_of_session'),
    path('JOLD/Thanks', views.joldThanks, name='JOLD_thanks')
]

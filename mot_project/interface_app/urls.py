from django.urls import path
from . import views

urlpatterns = [
    # path('/<int:res>/<int:nb>', views.save_results)'
    # it's important to separate `home` and `extension` by '-' !!!
    path('jold_ll', views.home, name='home-jold_ll'),
    path('jold_mot', views.home, name='home-jold_mot'),
    path('zpdes_mot', views.home, name='home-zpdes_mot'),

    path('', views.home, name='home'),
    path('home_user', views.home_user, name='home_user'),
    path('user_logout', views.user_logout, name='user_logout'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('consent_page', views.consent_page, name='consent_page'),
    path('app_2D', views.visual_2d_task, name='app_2D'),
    path('app_3D', views.visual_3d_task, name='app_3D'),
    path('app_MOT', views.MOT_task, name='app_MOT'),
    path('next_episode', views.next_episode, name='next_episode'),
    path('restart_episode', views.restart_episode, name='restart_episode'),

    ## JOLD urls
    path('joldSaveTrial_LL', views.joldSaveTrial_LL, name='JOLD_save_trial_LL'),
    path('joldEndSess', views.joldEndSess, name='JOLD_end_sess'),
    path('JOLD/lunar_lander', views.joldStartSess_LL, name='JOLD_lunar_lander'),
    path('JOLD/post_sess/', views.joldPostSess, name='JOLD_post_sess'),
    path('JOLD/post_sess/<int:num>/', views.joldPostSess, name='JOLD_post_sess'),
    path('JOLD/thanks', views.joldThanks, name='JOLD_thanks')
]

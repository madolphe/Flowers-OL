from django.views.generic import TemplateView
from django.urls import path
from . import views

urlpatterns = [
    # path('/<int:res>/<int:nb>', views.save_results)'
    path('', views.home, name='home'),
    path('super', views.home, name='home_super'),
    path('jold_ll', views.home, name='home_jold_ll'),
    path('jold_mot', views.home, name='home_jold_mot'),
    path('zpdes_mot', views.home, name='home_zpdes_mot'),
    path('home_user', views.home_user, name='home_user'),
    path('user_logout', views.user_logout, name='user_logout'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('app_2D', views.visual_2d_task, name='app_2D'),
    path('app_3D', views.visual_3d_task, name='app_3D'),
    path('app_MOT', views.MOT_task, name='app_MOT'),
    path('next_episode', views.next_episode, name='next_episode'),
    path('restart_episode', views.restart_episode, name='restart_episode'),
    ## JOLD urls
    path('app_LL', views.joldStartSess_LL, name='app_LL'),
    path('joldSaveTrial_LL', views.joldSaveTrial_LL, name='joldSaveTrial_LL'),
    path('joldEndSess', views.joldEndSess, name='joldEndSess'),
    path('joldConfidence', views.joldConfidence, name='joldConfidence'),
    path('joldThanks', views.joldThanks, name='joldThanks'),
]

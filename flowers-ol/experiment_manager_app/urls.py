from django.urls import path, re_path
from . import views
from django.utils import timezone
import datetime


urlpatterns = [
    # Interface urls
    path('', views.login_page, name='login_page'),
    re_path(r'^study=(.*)$', views.login_page, name='login_page'),
    path('home', views.home, name='home'),
    path('user_logout', views.user_logout, name='user_logout'),
    path('signup_page', views.signup_page, name='signup_page'),
    path('consent_page', views.consent_page, name='consent_page'),
    path('off_session_page', views.off_session_page, name='off_session_page'),
    path('start_task', views.start_task, name='start_task'),
    path('end_task', views.end_task, name='end_task'),
    path('thanks_page', views.thanks_page, name='thanks_page'),
    path('end_session', views.end_session, name='end_session'),

    # JOLD urls
    path('JOLD/practice-LL', views.jold_start_ll_practice, name='jold_start_ll_practice'),
    path('JOLD/save-trial', views.jold_save_ll_trial, name='jold_save_ll_trial'),
    path('JOLD/close-LL-practice', views.jold_close_ll_practice, name='jold_close_ll_practice'),
    path('JOLD/close-postsess-questionnaire', views.jold_close_postsess_questionnaire,
         name='jold_close_postsess_questionnaire'),
    path('JOLD/close-session', views.jold_free_choice, name='jold_free_choice'),
    path('JOLD/close-session/<int:choice>/', views.jold_free_choice, name='jold_free_choice')
]

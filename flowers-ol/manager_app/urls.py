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
    path('off_session_page/<str:case>/', views.off_session_page, name='off_session_page'),
    path('start_task', views.start_task, name='start_task'),
    path('end_task', views.end_task, name='end_task'),
    path('thanks_page', views.thanks_page, name='thanks_page'),
    path('end_session', views.end_session, name='end_session'),

    # Superuser urls
    path('fork_super', views.fork_super, name='fork_super'),
    path('home_super', views.home_super, name='home_super'),
    path('reset_user_participant', views.reset_user_participant, name='reset_user_participant')   
]

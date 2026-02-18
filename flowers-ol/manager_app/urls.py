from django.urls import path, re_path
from . import views
from django.utils import timezone
import datetime


urlpatterns = [
    # Interface urls
    path("", views.login_page, name="login_page"),
    re_path(r"^study=(.*)$", views.login_page, name="login_page"),
    path("home", views.home, name="home"),
    path("user_logout", views.user_logout, name="user_logout"),
    path("signup_page", views.signup_page, name="signup_page"),
    path(
        "off_session_page/<str:case>/", views.off_session_page, name="off_session_page"
    ),
    path("start_task", views.start_task, name="start_task"),
    path("end_task", views.end_task, name="end_task"),
    path("thanks_page", views.thanks_page, name="thanks_page"),
    path("end_session", views.end_session, name="end_session"),
    # Superuser urls
    path("admin_login/", views.admin_login_page, name="admin_login"),
    path("admin_home", views.admin_home, name="admin_home"),
    path("admin_home/<str:pannel_name>/", views.admin_home, name="admin_pannel"),
    path("admin_myprofile", views.admin_myprofile, name="admin_myprofile"),
    path("reset_stack", views.reset_stack, name="reset_stack"),
    path(
        "reset_user_participant",
        views.reset_user_participant,
        name="reset_user_participant",
    ),
    path("switch_participant", views.switch_participant, name="switch_participant"),
    path(
        "admin_change_user_password",
        views.admin_change_user_password,
        name="admin_change_user_password",
    ),
    path("logout/", views.logout_admin, name="logout"),
]

from django.urls import path
from . import views

urlpatterns = [
    path('demo_questionnaire', views.demo_questionnaire, name='demo_questionnaire'),
    path('exit_demo_task', views.exit_demo_task, name='exit_demo_task'),
]
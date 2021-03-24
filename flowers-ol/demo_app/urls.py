from django.urls import path
from . import views

urlpatterns = [
    path('demo_questionnaire', views.demo_questionnaire, name='demo_questionnaire'),
]
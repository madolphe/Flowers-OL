from django.urls import path
from . import views

urlpatterns = [
    path('questionnaire', views.questionnaire, name='questionnaire')
]
from django.urls import path
from . import views

urlpatterns = [
    path('questionnaire', views.questionnaire, name='questionnaire'),
    path('consent_page', views.consent_page, name='consent_page'),
]
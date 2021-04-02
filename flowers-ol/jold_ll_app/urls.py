from django.urls import path
from . import views


urlpatterns = [
    path('JOLD/consent_page', views.jold_consent_page, name='jold_consent_page'),
    path('JOLD/practice-LL', views.jold_start_ll_practice, name='jold_start_ll_practice'),
    path('JOLD/save-trial', views.jold_save_ll_trial, name='jold_save_ll_trial'),
    path('JOLD/close-LL-practice', views.jold_close_ll_practice, name='jold_close_ll_practice'),
    path('JOLD/close-postsess-questionnaire', views.jold_close_postsess_questionnaire,
         name='jold_close_postsess_questionnaire'),
    path('JOLD/close-session', views.jold_free_choice, name='jold_free_choice'),
    path('JOLD/close-session/<int:choice>/', views.jold_free_choice, name='jold_free_choice'),
]

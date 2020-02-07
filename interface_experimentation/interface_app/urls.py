from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='menu'),
    path('task', views.visual_task, name='interface')
]

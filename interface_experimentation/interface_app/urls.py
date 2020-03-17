from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='menu'),
    path('app_2D', views.visual_2d_task, name='app_2D'),
    path('app_3D', views.visual_3d_task, name='app_3D'),
]

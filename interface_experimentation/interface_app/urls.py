from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='menu'),
    # path('/<int:res>/<int:nb>', views.save_results)'
    path('home_user', views.home_user, name='home_user'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('sign_in', views.sign_in, name='sign_in'),
    path('app_2D', views.visual_2d_task, name='app_2D'),
    path('app_3D', views.visual_3d_task, name='app_3D'),
]

from django.urls import path
from . import views

urlpatterns = [
    # path('/<int:res>/<int:nb>', views.save_results)'
    path('', views.home, name='home'),
    path('home_user', views.home_user, name='home_user'),
    path('user_logout', views.user_logout, name='user_logout'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('app_2D', views.visual_2d_task, name='app_2D'),
    path('app_3D', views.visual_3d_task, name='app_3D'),
    path('next_episode', views.next_episode, name='next_episode')
]

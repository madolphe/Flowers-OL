# from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime


def home(request):
    """ Exemple de page non valide au niveau HTML pour que l'exemple soit concis """
    return render(request, 'home.html', locals())


def visual_2d_task(request):
    return render(request, 'app_2D.html', locals())


def visual_3d_task(request):
    return render(request, 'app_3D.html', locals())



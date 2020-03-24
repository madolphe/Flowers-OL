from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import UserForm, ParticipantProfileForm
from django.contrib.auth.models import User
from django.db.models.signals import post_save


def sign_up(request):
    # First, init forms, if request is valid we can create the user
    form_user = UserForm(request.POST or None)
    form_profile = ParticipantProfileForm(request.POST or None)
    print('enter in sign_up')
    if form_user.is_valid() and form_profile.is_valid():
        last_name = form_user.cleaned_data['last_name']
        first_name = form_user.cleaned_data['first_name']
        password = form_user.cleaned_data['password']
        mail = form_user.cleaned_data['mail']
        birth_date = form_profile.cleaned_data['birth_date']
        # Add those information to user to create it:
        user = User.objects.create_user(last_name=last_name,
                                        first_name=first_name,
                                        password=password,
                                        email=mail,
                                        )
        user.save()
        # Redirect to user homepage:
        return redirect(home_user)
    return render(request, 'sign_up.html', {'form_profile': form_profile, 'form_user': form_user})


def home(request):
    """ Exemple de page non valide au niveau HTML pour que l'exemple soit concis """
    print(request.POST)
    print("return here")
    return render(request, 'home.html', locals())


def home_user(request):
    return render(request, 'home.html', locals())


def visual_2d_task(request):
    return render(request, 'app_2D.html', locals())


def visual_3d_task(request):
    return render(request, 'app_3D.html', locals())



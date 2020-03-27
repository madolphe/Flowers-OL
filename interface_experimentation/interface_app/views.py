# @TODO: add logout button
# @TODO: add sign_in directly on welcome page
# @TODO: ajax n episodes
# @TODO: test new design for frontend

from django.shortcuts import render, redirect
from .forms import UserForm, ParticipantProfileForm, SignInForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse


def sign_up(request):
    # First, init forms, if request is valid we can create the user
    form_user = UserForm(request.POST or None)
    form_profile = ParticipantProfileForm(request.POST or None)
    if form_user.is_valid() and form_profile.is_valid():
        # Get extra-info for user profile:
        user = form_user.save(commit=False)
        # Use set_password in order to hash password
        user.set_password(form_user.cleaned_data['password'])
        user.save()
        form_profile.save_profile(user)
        # Redirect to user homepage:
        login(request, user)
        return redirect(reverse(home_user))
    context = {'form_profile': form_profile, 'form_user': form_user}
    return render(request, 'sign_up.html', context)


def home(request):
    # First, init forms, if request is valid we check if the user exists
    print(request)
    error = False
    form_sign_in = SignInForm(request.POST or None)
    if form_sign_in.is_valid():
        username = form_sign_in.cleaned_data['username']
        password = form_sign_in.cleaned_data['password']
        user = authenticate(request, username=username, password=password)  # Check if datas are valid
        if user:  # if user exists
            login(request, user)  # connect user
            return redirect(reverse(home_user))
        else:  # sinon une erreur sera affichée
            error = True
    return render(request, 'home.html', locals())


@login_required
def home_user(request):
    if request.user.is_authenticated:
        context = "Salut, {0} !".format(request.user.username)
    return render(request, 'home_user.html', locals())


@login_required
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(reverse(home))


def visual_2d_task(request):
    return render(request, 'app_2D.html', locals())


def visual_3d_task(request):
    return render(request, 'app_3D.html', locals())



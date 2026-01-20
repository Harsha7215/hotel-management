from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm, LoginForm, UserProfileForm


#REGISTER VIEW
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


#LOGIN VIEW
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )
            return redirect("home")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


#LOGOUT VIEW
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


#USER PROFILE
@login_required
def profile(request):
    profile = request.user.userprofile

    if request.method == "POST":
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "accounts/profile.html", {"form": form})


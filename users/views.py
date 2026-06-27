from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

from .forms import RegistrationForm, LoginForm, ProfileEditForm
from .models import User
from utils.func_utils import get_page


def register(request):
    if request.user.is_authenticated:
        return redirect("projects:list")  
    form = RegistrationForm(request.POST or None)
    if not form.is_valid():
        return render(request, "users/register.html", {"form": form})
    user = form.save() 
    login(request, user)
    messages.success(request, "Регистрация прошла успешно!")
    return redirect("projects:list")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = LoginForm(request, data=request.POST or None)
    if not form.is_valid():
        return render(request, "users/login.html", {"form": form})
    user = form.get_user()
    login(request, user)
    messages.success(request, "Вы успешно вошли в систему!")
    return redirect("projects:list")


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из системы")
    return redirect("projects:list")


def user_details(request, user_id):
    user = get_object_or_404(User, pk=user_id, is_active=True)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile(request):
    form = ProfileEditForm(
        request.POST or None, 
        request.FILES or None, 
        instance=request.user
    )
    if not form.is_valid():
        return render(request, "users/edit_profile.html", {"form": form})
    form.save()
    messages.success(request, "Профиль успешно обновлен!")
    return redirect("users:details", user_id=request.user.pk)


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if not form.is_valid():
        return render(request, "users/change_password.html", {"form": form})
    user = form.save()
    update_session_auth_hash(request, user)
    messages.success(request, "Пароль успешно изменен!")
    return redirect("users:details", user_id=request.user.pk)


def user_list(request):
    participants = User.objects.filter(is_active=True)
    active_filter = request.GET.get("filter", "")
    query_prefix = f"filter={active_filter}&" if active_filter else ""

    if active_filter and request.user.is_authenticated:
        if active_filter == "owners-of-favorite-projects":
            participants = participants.filter(
                owned_projects__in=request.user.favorites.all()
            ).distinct()
        elif active_filter == "owners-of-participating-projects":
            participants = participants.filter(
                owned_projects__in=request.user.participated_projects.all()
            ).distinct()
        elif active_filter == "interested-in-my-projects":
            my_projects = request.user.owned_projects.all()
            participants = participants.filter(
                favorites__in=my_projects
            ).exclude(id=request.user.id).distinct()
        elif active_filter == "participants-of-my-projects":
            participants = participants.filter(
                participated_projects__in=request.user.owned_projects.all()
            ).distinct()

    page_obj = get_page(participants, request)
    context = {
        "page_obj": page_obj,
        "active_filter": active_filter,
        "query_prefix": query_prefix,
    }
    return render(request, "users/participants.html", context)

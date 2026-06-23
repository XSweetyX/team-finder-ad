from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import RegistrationForm, LoginForm, ProfileEditForm, CustomPasswordChangeForm
from .models import User


def register(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("projects:list")
    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Вы успешно вошли в систему!")
            return redirect("projects:list")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


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
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("users:details", user_id=request.user.pk)
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно изменен!")
            return redirect("users:details", user_id=request.user.pk)
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, "users/change_password.html", {"form": form})


def user_list(request):
    participants = User.objects.filter(is_active=True).order_by("-id")
    
    active_filter = request.GET.get("filter", "")
    query_prefix = f"filter={active_filter}&" if active_filter else ""

    if active_filter and request.user.is_authenticated:
        if active_filter == "owners-of-favorite-projects":
            # Авторы избранных мной проектов
            participants = participants.filter(
                owned_projects__in=request.user.favorites.all()
            ).distinct()

        elif active_filter == "owners-of-participating-projects":
            # Авторы проектов, в которых я участвую
            participants = participants.filter(
                owned_projects__in=request.user.participated_projects.all()
            ).distinct()

        elif active_filter == "interested-in-my-projects":
            # Пользователи, которым нравятся МОИ проекты (добавили в избранное)
            my_projects = request.user.owned_projects.all()
            participants = participants.filter(
                favorites__in=my_projects
            ).exclude(id=request.user.id).distinct()   # ← Исключаем себя

        elif active_filter == "participants-of-my-projects":
            # Участники МОИХ проектов
            participants = participants.filter(
                participated_projects__in=request.user.owned_projects.all()
            ).distinct()   # ← Исключаем себя

    # Пагинация
    paginator = Paginator(participants, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        'page_obj': page_obj,
        'participants': page_obj,
        'active_filter': active_filter,
        'query_prefix': query_prefix,
    }
    
    return render(request, "users/participants.html", context)
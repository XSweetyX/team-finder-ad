from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project
from utils.func_utils import get_page


def project_list(request):
    projects = Project.objects.select_related("owner").all()
    page_obj = get_page(projects, request)
    return render(request, "projects/project_list.html", {
        "page_obj": page_obj,
        "query_prefix": "",
    })


@login_required
def favorite_projects(request):
    projects = request.user.favorites.select_related("owner").all()
    page_obj = get_page(projects, request)
    return render(request, "projects/favorite_projects.html", {
        "projects": page_obj,
        "page_obj": page_obj,
    })


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    favorited = request.user.favorites.filter(pk=project.pk).exists()
    if favorited:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": not favorited})


def project_details(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    is_owner = request.user == project.owner
    if request.user.is_authenticated:
        is_participant = project.participants.filter(pk=request.user.pk).exists()
    else:
        is_participant = False
    context = {
        "project": project,
        "is_owner": is_owner,
        "is_participant": is_participant,
    }
    return render(request, "projects/project-details.html", context)


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if not form.is_valid():
        return render(request, "projects/create-project.html", {
            "form": form,
            "is_edit": False,
        })
    project = form.save(commit=False)
    project.owner = request.user
    project.save()
    project.participants.add(request.user)
    messages.success(request, "Проект успешно создан!")
    return redirect("projects:details", project_id=project.pk)


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        messages.error(request, "Только автор проекта может его редактировать.")
        return redirect("projects:list")       
    form = ProjectForm(request.POST or None, instance=project)
    if not form.is_valid():
        return render(request, "projects/create-project.html", {
            "form": form,
            "is_edit": True,
        })
    form.save()
    messages.success(request, "Проект успешно обновлен!")
    return redirect("projects:details", project_id=project.pk)


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Только автор может закрыть проект"},
            status=HTTPStatus.FORBIDDEN,
        )
    if project.is_open:
        project.status = project.STATUS_CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": project.status})
    return JsonResponse(
        {"status": "error", "message": "Проект уже закрыт"},
        status=HTTPStatus.BAD_REQUEST,
    )


@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    is_currently_participant = project.participants.filter(
        pk=request.user.pk,
    ).exists()
    if is_currently_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({
        "status": "ok",
        "participant": not is_currently_participant,
        "participants_count": project.participants.count(),
    })

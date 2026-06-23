from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Project
from .forms import ProjectForm


def project_list(request):
    projects = Project.objects.select_related("owner").all().order_by("-created_at")

    paginator = Paginator(projects, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)


    return render(request, "projects/project_list.html", {
        "page_obj": page_obj,
        "query_prefix": "",
    })

@login_required
def favorite_projects(request):
    projects = request.user.favorites.select_related("owner").all().order_by("-created_at")

    paginator = Paginator(projects, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "projects/favorite_projects.html", {"projects": page_obj})


@login_required
def toggle_favorite(request, project_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

    project = get_object_or_404(Project, pk=project_id)

    if project in request.user.favorites.all():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True

    return JsonResponse({"status": "ok", "favorited": favorited})


def project_details(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id
    )

    is_owner = request.user == project.owner
    is_participant = project.participants.filter(
        pk=request.user.pk).exists() if request.user.is_authenticated else False

    context = {
        "project": project,
        "is_owner": is_owner,
        "is_participant": is_participant,
    }
    return render(request, "projects/project-details.html", context)


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            messages.success(request, "Проект успешно создан!")
            return redirect("projects:details", project_id=project.pk)
    else:
        form = ProjectForm()

    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Проект успешно обновлен!")
            return redirect("projects:details", project_id=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
def complete_project(request, project_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

    project = get_object_or_404(Project, pk=project_id, owner=request.user)

    if project.status == "open":
        project.status = "closed"
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})

    return JsonResponse({"status": "error", "message": "Project is already closed"}, status=400)


@login_required
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем, является ли пользователь участником
    is_currently_participant = request.user in project.participants.all()
    
    if is_currently_participant:
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    
    return JsonResponse({
        'status': 'ok',
        'participant': participant,           # ← именно это ожидает твой JS
        'participants_count': project.participants.count()
    })
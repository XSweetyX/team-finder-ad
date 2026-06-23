from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "name", "surname", "is_active", "is_staff", "created_at"]
    list_filter = ["is_active", "is_staff", "created_at"]
    search_fields = ["email", "name", "surname"]
    ordering = ["-created_at"]

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional info", {"fields": ("name", "surname", "avatar", "phone", "github_url", "about")}),
        ("Favorites", {"fields": ("favorites",)}),
    )
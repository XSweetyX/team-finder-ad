from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "surname", "password1", "password2"),
        }),
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name", "surname", "avatar", "phone", "github_url", "about")}),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Favorites", {"fields": ("favorites",)}),
    )

    readonly_fields = ("created_at", "last_login")

    list_display = ["email", "name", "surname", "is_active", "is_staff", "created_at"]
    list_filter = ["is_active", "is_staff", "created_at"]
    search_fields = ["email", "name", "surname"]
    ordering = ["-created_at"]

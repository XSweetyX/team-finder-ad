from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("list/", views.user_list, name="list"),
    path("<int:user_id>/", views.user_details, name="details"),
    path("edit-profile/", views.edit_profile, name="edit"),
    path("change-password/", views.change_password, name="change_password"),

]


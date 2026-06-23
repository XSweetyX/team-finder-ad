from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User
import re


class RegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=124, required=True, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Имя"
    }))
    surname = forms.CharField(max_length=124, required=True, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Фамилия"
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Email"
    }))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Пароль"
    }))
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Подтверждение пароля"
    }))

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже зарегистрирован")
        return email


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Email"
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Пароль"
    }))

    def clean(self):
        cleaned_data = super().clean()
        if not self.user_cache:
            raise forms.ValidationError("Неверный имейл или пароль")
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    name = forms.CharField(max_length=124, required=True, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    surname = forms.CharField(max_length=124, required=True, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    avatar = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={
        "class": "form-control"
    }))
    about = forms.CharField(required=False, widget=forms.Textarea(attrs={
        "class": "form-control",
        "rows": 3
    }))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "+7XXXXXXXXXX"
    }))
    github_url = forms.URLField(required=False, widget=forms.URLInput(attrs={
        "class": "form-control",
        "placeholder": "https://github.com/username"
    }))

    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return phone

        digits = "".join(filter(str.isdigit, phone))

        if not (re.match(r"^8\d{10}$", phone) or re.match(r"^\+7\d{10}$", phone)):
            raise forms.ValidationError("Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")

        if len(digits) == 11 and digits.startswith("8"):
            phone = f"+7{digits[1:]}"
        elif len(digits) == 10:
            phone = f"+7{digits}"

        if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот номер телефона уже используется")

        return phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        if github_url and "github.com" not in github_url:
            raise forms.ValidationError("Ссылка должна вести на GitHub")
        return github_url


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Старый пароль"
    }))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Новый пароль"
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Подтверждение нового пароля"
    }))
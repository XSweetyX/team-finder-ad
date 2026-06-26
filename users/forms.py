import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User
from utils.validators import validate_github_url
from constants import FORM_MAX_LENGTH


class RegistrationForm(UserCreationForm):
    name = forms.CharField(
        max_length=FORM_MAX_LENGTH,
        required=True,
        label="Имя",
        widget=forms.TextInput(attrs={"placeholder": "Имя"})
    )
    surname = forms.CharField(
        max_length=FORM_MAX_LENGTH,
        required=True,
        label="Фамилия",
        widget=forms.TextInput(attrs={"placeholder": "Фамилия"})
    )
    email = forms.EmailField(
        required=True,
        label="Электронная почта", 
        widget=forms.EmailInput(attrs={"placeholder": "Электронная почта"})
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Пароль"})
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"placeholder": "Подтверждение пароля"})
    )

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password1", "password2"]




class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(attrs={"placeholder": "Электронная почта"})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Пароль"})
    )

    def clean(self):
        cleaned_data = super().clean()
        if not self.user_cache:
            raise forms.ValidationError("Неверный имейл или пароль")
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)
    about = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "+7XXXXXXXXXX"})
    )
    github_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={"placeholder": "https://github.com/username"})
    )

    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return phone

        digits = "".join(filter(str.isdigit, phone))

       
        pattern_8 = r"^8\d{10}$"
        pattern_7 = r"^\+7\d{10}$"
        if not (re.match(pattern_8, phone) or re.match(pattern_7, phone)):
            msg = "Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            raise forms.ValidationError(msg)

        if len(digits) == 11 and digits.startswith("8"):
            phone = f"+7{digits[1:]}"
        elif len(digits) == 10:
            phone = f"+7{digits}"

        if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот номер телефона уже используется")
        return phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        
        return validate_github_url(github_url)


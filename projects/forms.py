from django import forms

from .models import Project
from utils.validators import validate_github_url
from constants import FORM_MAX_LENGTH


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
                'name': forms.TextInput(attrs={
                    'placeholder': 'Название проекта'
                }),
                'description': forms.Textarea(attrs={
                    'placeholder': 'Описание проекта'
                }),
                'github_url': forms.URLInput(attrs={
                    'placeholder': 'https://github.com/username/project'
                }),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        return validate_github_url(github_url)

from django import forms

from .models import Project
from utils.validators import validate_github_url
from constants import FORM_MAX_LENGTH


class ProjectForm(forms.ModelForm):
    name = forms.CharField(max_length=FORM_MAX_LENGTH, required=True,
        label="Название проекта", 
        widget=forms.TextInput(attrs={
            "placeholder": "Название проекта"
        }))
    description = forms.CharField(required=False,
        label="Описание проекта",
        widget=forms.Textarea(attrs={
            "placeholder": "Описание проекта"
        }))
    github_url = forms.URLField(required=False,
        label="Ссылка на Github",
        widget=forms.URLInput(attrs={
            "placeholder": "https://github.com/username/project"
        }))
    status = forms.ChoiceField(
        label="Cтатус проекта",
        choices=Project.STATUS_CHOICES,
    )

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        
       
        return  validate_github_url(github_url)


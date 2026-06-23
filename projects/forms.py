from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    name = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Название проекта"
    }))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        "class": "form-control",
        "rows": 5,
        "placeholder": "Описание проекта"
    }))
    github_url = forms.URLField(required=False, widget=forms.URLInput(attrs={
        "class": "form-control",
        "placeholder": "https://github.com/username/project"
    }))
    status = forms.ChoiceField(
        choices=Project.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        if github_url and "github.com" not in github_url:
            raise forms.ValidationError("Ссылка должна вести на GitHub")
        return github_url
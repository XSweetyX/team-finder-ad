from django import forms


def validate_github_url(value):
    """Проверяет, что ссылка ведет на GitHub."""
    if value and "github.com" not in value:
        raise forms.ValidationError("Ссылка должна вести на GitHub")
    return value


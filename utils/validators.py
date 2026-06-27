from urllib.parse import urlparse

from django import forms


def validate_github_url(value):
    if not value:
        return value    
    try:
        parsed_url = urlparse(value)
        if parsed_url.netloc != "github.com":
            raise forms.ValidationError("Ссылка должна вести на github.com")
    except ValueError:
        raise forms.ValidationError("Некорректный формат URL") 
    return value

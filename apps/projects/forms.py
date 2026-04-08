from django import forms

from apps.projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "tech_stack"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input form-textarea", "rows": 4}),
            "tech_stack": forms.TextInput(attrs={"class": "form-input"}),
        }

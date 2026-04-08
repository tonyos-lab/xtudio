from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(forms.Form):
    first_name = forms.CharField(
        max_length=150, required=False, widget=forms.TextInput(attrs={"class": "form-input"})
    )
    last_name = forms.CharField(
        max_length=150, required=False, widget=forms.TextInput(attrs={"class": "form-input"})
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-input"}))
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self) -> dict:
        cleaned_data = super().clean()
        if cleaned_data:
            pw = cleaned_data.get("password")
            pw_confirm = cleaned_data.get("password_confirm")
            if pw and pw_confirm and pw != pw_confirm:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned_data or {}


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-input"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-input"}))


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "bio", "avatar"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input"}),
            "last_name": forms.TextInput(attrs={"class": "form-input"}),
            "bio": forms.Textarea(attrs={"class": "form-input form-textarea", "rows": 4}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-input"}),
        }

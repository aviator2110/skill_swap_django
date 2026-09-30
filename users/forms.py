from users.models import User
from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(
        label="Username",
        min_length=3,
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your username",
        })
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your email",
        })
    )
    password = forms.CharField(
        label="Password",
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter your password",
        })
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirm your password",
        })
    )
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        if User.objects.filter(username=cleaned_data.get("username")).exists():
            raise forms.ValidationError("Username already exists")
        if User.objects.filter(email=cleaned_data.get("email")).exists():
            raise forms.ValidationError("Email already exists")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your username",
        })
    )
    password = forms.CharField(
        label="Password",
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter your password",
        })
    )
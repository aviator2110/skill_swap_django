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
        label="Username or email",
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your username or email",
        })
    )
    password = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter your password",
        })
    )


class ProfileEditForm(forms.Form):
    avatar = forms.ImageField(
        label="Avatar",
        required=False,
        widget=forms.FileInput(attrs={
            "placeholder": "Upload your avatar",
        })
    )
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
    first_name = forms.CharField(
        label="First Name",
        required=False,
        min_length=2,
        max_length=50,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your first name",
        })
    )
    last_name = forms.CharField(
        label="Last Name",
        required=False,
        min_length=2,
        max_length=50,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your last name",
        })
    )
    bio = forms.CharField(
        label="Bio",
        required=False,
        max_length=1000,
        widget=forms.Textarea(attrs={
            "placeholder": "Enter your bio",
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        users = User.objects.all()
        if self.user:
            users = users.exclude(pk=self.user.pk)

        if username and users.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        if email and users.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return cleaned_data
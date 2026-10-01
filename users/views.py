from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.db.models import Q
from .forms import RegisterForm, LoginForm
from .models import User


def Register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def Login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = User.objects.filter(
                Q(username=username_or_email) | Q(email=username_or_email)
            ).first()

            if user is not None:
                authenticated_user = authenticate(
                    request, username=user.username, password=password
                )
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    return redirect('/')

            form.add_error(None, 'Invalid username/email or password')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})
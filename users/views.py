from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import RegisterForm, LoginForm, ProfileEditForm
from .models import User


def Register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('profile')
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
                    return redirect('profile')

            form.add_error(None, 'Invalid username/email or password')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def Logout_view(request):
    logout(request)
    return redirect('login')


def profile_view(request, username=None):
    if username is None:
        if not request.user.is_authenticated:
            return redirect('login')
        target_user = request.user
        is_own_profile = True
    else:
        target_user = get_object_or_404(User, username=username)
        is_own_profile = request.user.is_authenticated and (request.user == target_user)

    if is_own_profile:
        user_offers = target_user.offers.select_related('category', 'level', 'format', 'status').order_by('-created_at')
    else:
        user_offers = target_user.offers.filter(status__slug='published').select_related('category', 'level', 'format', 'status').order_by('-created_at')

    from offers.models import Review
    teacher_reviews = Review.objects.filter(offer__author=target_user).select_related('author', 'offer').order_by('-created_at')

    context = {
        'profile_user': target_user,
        'is_own_profile': is_own_profile,
        'user_offers': user_offers,
        'teacher_reviews': teacher_reviews,
    }
    return render(request, 'users/profile.html', context)



def profile_edit_view(request, username:str):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            user = request.user
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.bio = form.cleaned_data['bio']

            avatar = form.cleaned_data.get('avatar')
            if avatar:
                user.avatar = avatar

            user.save()
            return redirect('profile')
    else:
        form = ProfileEditForm(
            initial={
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'bio': request.user.bio,
            },
            user=request.user
        )

    return render(request, 'users/profile_edit.html', {'form': form})
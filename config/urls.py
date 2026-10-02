from django.contrib import admin
from django.urls import path
from users import views as users_views

urlpatterns = [
    path('login/', users_views.Login_view, name='login'),
    path('register/', users_views.Register_view, name='register'),
    path('profile/', users_views.profile_view, name='profile'),
    path('profile/edit/', users_views.profile_edit_view, name='profile_edit'),
]    

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.Login_view, name='login'),
    path('register/', views.Register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/<str:username>/', views.profile_edit_view, name='profile_edit'),
    path('logout/', views.Logout_view, name='logout'),
]
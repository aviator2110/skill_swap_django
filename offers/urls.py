from django.urls import path
from . import views

urlpatterns = [
    path('', views.explore_view, name='explore'),
    path('offers/<int:pk>/', views.offer_detail_view, name='offer_detail'),
    path('mentors/', views.mentors_view, name='mentors'),
]


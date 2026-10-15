from django.urls import path
from . import views

urlpatterns = [
    path('', views.explore_view, name='explore'),
    path('offers/create/', views.offer_create_view, name='offer_create'),
    path('offers/<int:pk>/', views.offer_detail_view, name='offer_detail'),
    path('offers/<int:pk>/edit/', views.offer_edit_view, name='offer_edit'),
    path('offers/<int:pk>/delete/', views.offer_delete_view, name='offer_delete'),
    path('offers/<int:pk>/book/', views.booking_create_view, name='booking_create'),
    path('my-offers/', views.my_offers_view, name='my_offers'),
    path('my-requests/', views.my_requests_view, name='my_requests'),
    path('requests/<int:pk>/<str:action>/', views.booking_status_update_view, name='booking_status_update'),
    path('mentors/', views.mentors_view, name='mentors'),
]

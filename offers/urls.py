from django.urls import path
from . import views

urlpatterns = [
    path('', views.explore_view, name='explore'),
    path('popular/', views.popular_view, name='popular'),
    path('offers/create/', views.offer_create_view, name='offer_create'),
    path('offers/<int:pk>/', views.offer_detail_view, name='offer_detail'),
    path('offers/<int:pk>/edit/', views.offer_edit_view, name='offer_edit'),
    path('offers/<int:pk>/delete/', views.offer_delete_view, name='offer_delete'),
    path('offers/<int:pk>/book/', views.booking_create_view, name='booking_create'),
    path('offers/<int:pk>/favorite/', views.favorite_toggle_view, name='favorite_toggle'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('my-offers/', views.my_offers_view, name='my_offers'),
    path('my-requests/', views.my_requests_view, name='my_requests'),
    path('requests/<int:booking_id>/review/', views.review_create_view, name='review_create'),
    path('requests/<int:pk>/<str:action>/', views.booking_status_update_view, name='booking_status_update'),
    path('reviews/<int:pk>/edit/', views.review_edit_view, name='review_edit'),
    path('reviews/<int:pk>/delete/', views.review_delete_view, name='review_delete'),
    path('mentors/', views.mentors_view, name='mentors'),
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/offers/<int:pk>/<str:action>/', views.admin_offer_moderate_view, name='admin_offer_moderate'),
    path('admin-panel/users/<int:pk>/<str:action>/', views.admin_user_ban_view, name='admin_user_ban'),
    path('admin-panel/reviews/<int:pk>/delete/', views.admin_review_delete_action_view, name='admin_review_delete_action'),
]

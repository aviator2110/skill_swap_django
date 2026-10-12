from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Offer

User = get_user_model()


def explore_view(request):
    offers = (
        Offer.objects.filter(status__slug='published')
        .select_related('author', 'category', 'level', 'format', 'status')
        .order_by('-created_at')
    )
    return render(request, 'offers/explore.html', {'offers': offers})


def offer_detail_view(request, pk):
    offer = get_object_or_404(
        Offer.objects.select_related('author', 'category', 'level', 'format', 'status'),
        pk=pk
    )
    reviews = offer.reviews.select_related('author').order_by('-created_at')
    
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = offer.is_favorited_by(request.user)

    context = {
        'offer': offer,
        'reviews': reviews,
        'is_favorited': is_favorited,
    }
    return render(request, 'offers/offer_detail.html', context)


def mentors_view(request):
    mentors = (
        User.objects.filter(offers__status__slug='published')
        .distinct()
        .order_by('-date_joined')
    )
    return render(request, 'offers/mentors.html', {'mentors': mentors})


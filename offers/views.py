from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from .models import Offer, Status, BookingRequest, Review, Favorite
from .forms import OfferForm, BookingRequestForm, ReviewForm

User = get_user_model()


def explore_view(request):
    offers = (
        Offer.objects.filter(status__slug='published')
        .select_related('author', 'category', 'level', 'format', 'status')
        .order_by('-created_at')
    )
    favorited_ids = set()
    if request.user.is_authenticated:
        favorited_ids = set(request.user.favorites.values_list('offer_id', flat=True))

    return render(request, 'offers/explore.html', {
        'offers': offers,
        'favorited_ids': favorited_ids,
    })


def offer_detail_view(request, pk):
    offer = get_object_or_404(
        Offer.objects.select_related('author', 'category', 'level', 'format', 'status'),
        pk=pk
    )
    reviews = offer.reviews.select_related('author').order_by('-created_at')
    
    is_favorited = False
    is_author = False
    active_booking = None
    can_book = False
    booking_form = None

    if request.user.is_authenticated:
        is_favorited = offer.is_favorited_by(request.user)
        is_author = (request.user == offer.author)
        active_booking = BookingRequest.objects.filter(
            offer=offer,
            student=request.user,
            status__in=[BookingRequest.Status.PENDING, BookingRequest.Status.ACCEPTED]
        ).first()
        can_book = (not is_author) and request.user.can_book and (active_booking is None)
        if can_book:
            booking_form = BookingRequestForm()

    context = {
        'offer': offer,
        'reviews': reviews,
        'is_favorited': is_favorited,
        'is_author': is_author,
        'active_booking': active_booking,
        'can_book': can_book,
        'booking_form': booking_form,
    }
    return render(request, 'offers/offer_detail.html', context)


def mentors_view(request):
    mentors = (
        User.objects.filter(offers__status__slug='published')
        .distinct()
        .order_by('-date_joined')
    )
    return render(request, 'offers/mentors.html', {'mentors': mentors})


@login_required
def booking_create_view(request, pk):
    offer = get_object_or_404(Offer, pk=pk, status__slug='published')

    if offer.author == request.user:
        messages.error(request, "You cannot send a booking request to your own offer.")
        return redirect('offer_detail', pk=pk)

    if not request.user.can_book:
        messages.error(request, "Your account is restricted from booking lessons.")
        return redirect('offer_detail', pk=pk)

    has_active = BookingRequest.objects.filter(
        offer=offer,
        student=request.user,
        status__in=[BookingRequest.Status.PENDING, BookingRequest.Status.ACCEPTED]
    ).exists()

    if has_active:
        messages.warning(request, "You already have an active request for this lesson.")
        return redirect('offer_detail', pk=pk)

    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.offer = offer
            booking.student = request.user
            booking.status = BookingRequest.Status.PENDING
            booking.save()
            messages.success(request, f"Booking request for '{offer.title}' sent successfully!")
            return redirect('my_requests')
        else:
            messages.error(request, "Could not submit booking request. Please check your message.")
    
    return redirect('offer_detail', pk=pk)


@login_required
def my_requests_view(request):
    incoming_requests = (
        BookingRequest.objects.filter(offer__author=request.user)
        .select_related('offer', 'student', 'review')
        .order_by('-created_at')
    )
    outgoing_requests = (
        BookingRequest.objects.filter(student=request.user)
        .select_related('offer', 'offer__author', 'review')
        .order_by('-created_at')
    )
    context = {
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
    }
    return render(request, 'offers/my_requests.html', context)


@login_required
def booking_status_update_view(request, pk, action):
    booking = get_object_or_404(
        BookingRequest.objects.select_related('offer', 'student', 'offer__author'),
        pk=pk
    )

    is_teacher = bool(request.user == booking.offer.author or request.user.is_admin_user)
    is_student = bool(request.user == booking.student or request.user.is_admin_user)

    if action == 'accept':
        if not is_teacher:
            return HttpResponseForbidden("Only the lesson author can accept requests.")
        if booking.status != BookingRequest.Status.PENDING:
            messages.error(request, "Only pending requests can be accepted.")
        else:
            booking.status = BookingRequest.Status.ACCEPTED
            booking.save()
            messages.success(request, f"Accepted request from {booking.student.username}.")

    elif action == 'reject':
        if not is_teacher:
            return HttpResponseForbidden("Only the lesson author can reject requests.")
        if booking.status != BookingRequest.Status.PENDING:
            messages.error(request, "Only pending requests can be rejected.")
        else:
            booking.status = BookingRequest.Status.REJECTED
            booking.save()
            messages.info(request, f"Rejected request from {booking.student.username}.")

    elif action == 'complete':
        if not is_teacher:
            return HttpResponseForbidden("Only the lesson author can mark lessons as completed.")
        if booking.status != BookingRequest.Status.ACCEPTED:
            messages.error(request, "Only accepted lessons can be marked as completed.")
        else:
            booking.status = BookingRequest.Status.COMPLETED
            booking.save()
            messages.success(request, f"Lesson with {booking.student.username} marked as completed!")

    elif action == 'cancel':
        if not is_student:
            return HttpResponseForbidden("Only the requesting student can cancel this request.")
        if booking.status != BookingRequest.Status.PENDING:
            messages.error(request, "Only pending requests can be cancelled.")
        else:
            booking.status = BookingRequest.Status.CANCELLED
            booking.save()
            messages.info(request, "Booking request cancelled.")

    else:
        messages.error(request, "Invalid action.")

    return redirect('my_requests')


@login_required
def review_create_view(request, booking_id):
    booking = get_object_or_404(
        BookingRequest.objects.select_related('offer', 'student', 'offer__author'),
        pk=booking_id
    )

    if booking.student != request.user:
        return HttpResponseForbidden("Only the student who completed the lesson can leave a review.")

    if booking.status != BookingRequest.Status.COMPLETED:
        messages.error(request, "Reviews can only be left for completed lessons.")
        return redirect('my_requests')

    if hasattr(booking, 'review'):
        messages.info(request, "You have already reviewed this lesson.")
        return redirect('review_edit', pk=booking.review.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.author = request.user
            review.offer = booking.offer
            review.save()
            messages.success(request, f"Thank you for reviewing '{booking.offer.title}'!")
            return redirect('offer_detail', pk=booking.offer.pk)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'booking': booking,
        'offer': booking.offer,
        'is_edit': False,
    }
    return render(request, 'offers/review_form.html', context)


@login_required
def review_edit_view(request, pk):
    review = get_object_or_404(
        Review.objects.select_related('booking', 'offer', 'author'),
        pk=pk
    )

    if review.author != request.user:
        return HttpResponseForbidden("You can only edit your own reviews.")

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated.")
            return redirect('offer_detail', pk=review.offer.pk)
    else:
        form = ReviewForm(instance=review)

    context = {
        'form': form,
        'booking': review.booking,
        'offer': review.offer,
        'is_edit': True,
        'review': review,
    }
    return render(request, 'offers/review_form.html', context)


@login_required
def review_delete_view(request, pk):
    review = get_object_or_404(
        Review.objects.select_related('offer', 'author'),
        pk=pk
    )

    if review.author != request.user and not request.user.is_admin_user:
        return HttpResponseForbidden("You do not have permission to delete this review.")

    offer_pk = review.offer.pk

    if request.method == 'POST':
        review.delete()
        messages.success(request, "Review deleted successfully.")
        return redirect('offer_detail', pk=offer_pk)

    return render(request, 'offers/review_confirm_delete.html', {'review': review, 'offer': review.offer})




@login_required
def my_offers_view(request):
    offers = (
        request.user.offers.select_related('category', 'level', 'format', 'status')
        .order_by('-created_at')
    )
    return render(request, 'offers/my_offers.html', {'offers': offers})


@login_required
def offer_create_view(request):
    if not request.user.can_create_offers:
        messages.error(request, "Your account is restricted from creating new offers.")
        return redirect('my_offers')

    if request.method == 'POST':
        form = OfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.author = request.user

            if 'save_draft' in request.POST:
                offer.status = Status.objects.filter(slug='draft').first()
                messages.success(request, "Offer saved as draft.")
            else:
                offer.status = Status.objects.filter(slug='pending').first()
                messages.success(request, "Offer submitted for administrator review.")

            offer.save()
            return redirect('my_offers')
    else:
        form = OfferForm()

    return render(request, 'offers/offer_form.html', {'form': form, 'is_edit': False})


@login_required
def offer_edit_view(request, pk):
    offer = get_object_or_404(Offer, pk=pk)

    if offer.author != request.user and not request.user.is_admin_user:
        return HttpResponseForbidden("You do not have permission to edit this offer.")

    if request.user == offer.author and not request.user.can_create_offers:
        messages.error(request, "Your account is restricted from updating offers.")
        return redirect('my_offers')

    if request.method == 'POST':
        form = OfferForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            was_published = bool(offer.status and offer.status.slug == 'published')
            updated_offer = form.save(commit=False)

            if was_published and not request.user.is_admin_user:
                updated_offer.status = Status.objects.filter(slug='pending').first()
                messages.warning(request, "Changes saved. As this offer was published, it has been resubmitted for admin review.")
            elif 'save_draft' in request.POST:
                updated_offer.status = Status.objects.filter(slug='draft').first()
                messages.success(request, "Offer saved as draft.")
            elif offer.status and offer.status.slug in ['draft', 'rejected']:
                updated_offer.status = Status.objects.filter(slug='pending').first()
                messages.success(request, "Offer submitted for administrator review.")
            else:
                messages.success(request, "Offer updated successfully.")

            updated_offer.save()
            return redirect('offer_detail', pk=updated_offer.pk)
    else:
        form = OfferForm(instance=offer)

    return render(request, 'offers/offer_form.html', {'form': form, 'is_edit': True, 'offer': offer})


@login_required
def offer_delete_view(request, pk):
    offer = get_object_or_404(Offer, pk=pk)

    if offer.author != request.user and not request.user.is_admin_user:
        return HttpResponseForbidden("You do not have permission to delete this offer.")

    if request.method == 'POST':
        offer.delete()
        messages.success(request, "Offer deleted successfully.")
        return redirect('my_offers')

    return render(request, 'offers/offer_confirm_delete.html', {'offer': offer})


@login_required
def favorite_toggle_view(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    offer = get_object_or_404(Offer, pk=pk, status__slug='published')
    favorite = Favorite.objects.filter(user=request.user, offer=offer).first()

    if favorite:
        favorite.delete()
        messages.info(request, f"Removed '{offer.title}' from your favorites.")
    else:
        Favorite.objects.create(user=request.user, offer=offer)
        messages.success(request, f"Added '{offer.title}' to your favorites!")

    next_url = request.POST.get('next')
    if next_url and next_url.startswith('/'):
        return redirect(next_url)
    return redirect('offer_detail', pk=offer.pk)


@login_required
def favorites_view(request):
    favorites = (
        request.user.favorites.filter(offer__status__slug='published')
        .select_related('offer', 'offer__author', 'offer__category', 'offer__level', 'offer__format', 'offer__status')
        .order_by('-created_at')
    )
    return render(request, 'offers/favorites.html', {'favorites': favorites})




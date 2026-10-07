from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField


class Category(models.Model):
    name = models.CharField("Name", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=100, unique=True, blank=True)
    description = models.TextField("Description", blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Level(models.Model):
    name = models.CharField("Name", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Level"
        verbose_name_plural = "Levels"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Format(models.Model):
    name = models.CharField("Name", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Format"
        verbose_name_plural = "Formats"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Status(models.Model):
    name = models.CharField("Name", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Offer(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name="Author"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='offers',
        verbose_name="Category"
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.PROTECT,
        related_name='offers',
        verbose_name="Level"
    )
    format = models.ForeignKey(
        Format,
        on_delete=models.PROTECT,
        related_name='offers',
        verbose_name="Format"
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name='offers',
        verbose_name="Status"
    )
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Description")
    cover_image = CloudinaryField(
        "cover_image",
        blank=True,
        null=True
    )
    duration_minutes = models.PositiveIntegerField(
        "Duration (minutes)",
        default=60,
        help_text="Duration of lesson in minutes"
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        result = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(result, 1) if result is not None else None

    @property
    def reviews_count(self):
        return self.reviews.count()

    @property
    def completed_sessions_count(self):
        return self.booking_requests.filter(status=BookingRequest.Status.COMPLETED).count()

    @property
    def is_published(self):
        return bool(self.status and self.status.slug == 'published')

    def is_favorited_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.favorites.filter(user=user).exists()


class BookingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='booking_requests',
        verbose_name="Offer"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='booking_requests',
        verbose_name="Student"
    )
    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    message = models.TextField("Message", blank=True)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "Booking Request"
        verbose_name_plural = "Booking Requests"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'offer'],
                condition=models.Q(status__in=['pending', 'accepted']),
                name='unique_active_booking_request'
            )
        ]

    def __str__(self):
        return f"Request by {self.student.username} for {self.offer.title} ({self.get_status_display()})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.student_id and self.offer_id and self.student_id == self.offer.author_id:
            raise ValidationError("You cannot send a booking request to your own offer.")
        if self.student_id and getattr(self.student, 'is_banned', False):
            raise ValidationError("Banned users cannot make booking requests.")
        if self.status in [self.Status.PENDING, self.Status.ACCEPTED]:
            active = BookingRequest.objects.filter(
                student_id=self.student_id,
                offer_id=self.offer_id,
                status__in=[self.Status.PENDING, self.Status.ACCEPTED]
            )
            if self.pk:
                active = active.exclude(pk=self.pk)
            if active.exists():
                raise ValidationError("You already have an active request for this offer.")


class Review(models.Model):
    booking = models.OneToOneField(
        BookingRequest,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name="Booking Request"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_written',
        verbose_name="Author"
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Offer"
    )
    rating = models.PositiveSmallIntegerField(
        "Rating",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    comment = models.TextField("Comment")
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']

    def __str__(self):
        return f"Review ({self.rating}/5) by {self.author.username} for {self.offer.title}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.booking_id:
            if self.booking.status != BookingRequest.Status.COMPLETED:
                raise ValidationError("Reviews can only be left for completed lessons.")
            if self.booking.student_id != self.author_id:
                raise ValidationError("Only the student who completed the lesson can leave a review.")
            if self.booking.offer_id != self.offer_id:
                raise ValidationError("Review offer does not match booking offer.")

    def save(self, *args, **kwargs):
        if self.booking_id:
            if not self.author_id:
                self.author = self.booking.student
            if not self.offer_id:
                self.offer = self.booking.offer
        super().save(*args, **kwargs)


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="User"
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="Offer"
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        ordering = ['-created_at']
        unique_together = ('user', 'offer')

    def __str__(self):
        return f"{self.user.username} saved {self.offer.title}"
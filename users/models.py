from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        ADMIN = 'admin', 'Admin'
        USER = 'user', 'User'
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )
    avatar = CloudinaryField(
        "avatar",
        blank=True,
        null=True
    )
    bio = models.TextField(
        "About me",
        blank=True
    )
    is_banned = models.BooleanField(
        "Banned", 
        default=False
    )
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-date_joined']

    def save(self, *args, **kwargs):
        if self.role == self.Role.SUPER_ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.Role.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser

    @property
    def is_admin_user(self):
        return self.role in [self.Role.ADMIN, self.Role.SUPER_ADMIN] or self.is_superuser or self.is_staff

    @property
    def can_create_offers(self):
        return self.is_authenticated and not self.is_banned

    @property
    def can_book(self):
        return self.is_authenticated and not self.is_banned

    @property
    def published_offers_count(self):
        return self.offers.filter(status__slug='published').count()

    @property
    def completed_lessons_count(self):
        from offers.models import BookingRequest
        return BookingRequest.objects.filter(
            offer__author=self,
            status=BookingRequest.Status.COMPLETED
        ).count()

    @property
    def average_rating(self):
        from offers.models import Review
        result = Review.objects.filter(offer__author=self).aggregate(models.Avg('rating'))['rating__avg']
        return round(result, 1) if result is not None else None
from django.db import models
from django.conf import settings
from django.utils.text import slugify
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
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Offer(models.Model):
    class Level(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'

    class Format(models.TextChoices):
        ONLINE = 'online', 'Online'
        OFFLINE = 'offline', 'Offline'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending', 'Pending'
        PUBLISHED = 'published', 'Published'
        REJECTED = 'rejected', 'Rejected'

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
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Description")
    cover_image = CloudinaryField(
        "cover_image",
        blank=True,
        null=True
    )
    level = models.CharField(
        "Level",
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER
    )
    format = models.CharField(
        "Format",
        max_length=20,
        choices=Format.choices,
        default=Format.ONLINE
    )
    duration_minutes = models.PositiveIntegerField(
        "Duration (minutes)",
        default=60,
        help_text="Duration of lesson in minutes"
    )
    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

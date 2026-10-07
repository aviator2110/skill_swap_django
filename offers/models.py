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


class Level(models.Model):
    name = models.CharField("Name", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Level"
        verbose_name_plural = "Levels"
        ordering = ['name']

    def __str__(self):
        return self.name


class Format(models.Model):
    name = models.CharField("Name", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Format"
        verbose_name_plural = "Formats"
        ordering = ['name']

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField("Name", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"
        ordering = ['name']

    def __str__(self):
        return self.name


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
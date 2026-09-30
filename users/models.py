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


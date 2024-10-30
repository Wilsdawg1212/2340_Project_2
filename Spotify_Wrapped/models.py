# Create your models here.

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        """Create a regular user."""
        if not email:
            raise ValueError("The Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Basic User Information
    email = models.EmailField(unique=True)  # For authentication
    username = models.CharField(max_length=50, unique=True)  # Display name
    password = models.CharField(max_length=128)  # Secure password storage

    # Spotify-Specific Information
    spotify_id = models.CharField(max_length=50, blank=True, null=True)  # Store user's Spotify ID
    access_token = models.TextField(blank=True, null=True)  # Spotify API token
    refresh_token = models.TextField(blank=True, null=True)  # Token to refresh access
    token_expires = models.DateTimeField(blank=True, null=True)  # Track token expiry

    # Metadata
    date_joined = models.DateTimeField(auto_now_add=True)  # Track when the user registered
    last_login = models.DateTimeField(auto_now=True)  # Track the most recent login
    is_active = models.BooleanField(default=True)  # Control account activation
    is_staff = models.BooleanField(default=False)  # Django admin access

    # Manager
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Authentication will be done via email
    REQUIRED_FIELDS = ['username']  # Required for creating a superuser

    def __str__(self):
        return self.email

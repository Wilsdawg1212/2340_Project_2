# Create your models here.
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth import get_user_model

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
    favorites = models.ManyToManyField('Wrap', related_name='favorited_by_users', blank=True)

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

User = get_user_model()

class Wrap(models.Model):
    wrap_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the wrap was created

    title = models.CharField(max_length=255, default='Untitled Wrap')  # Title for the wrap
    theme = models.CharField(max_length=50, default='space')  # Theme for the wrap
    theme_gifs = models.JSONField()
    time_range = models.CharField(max_length=20, choices=[  # Time range selection
        ('short_term', 'Last 4 Weeks'),
        ('medium_term', 'Last 6 Months'),
        ('long_term', 'All Time')
    ], default='medium_term')

    # Fields for Top Tracks
    top_tracks = models.JSONField()  # Use a JSONField to store track data as a list of dictionaries

    # Fields for Top Artists
    top_artists = models.JSONField()  # Use a JSONField to store artist data as a list of dictionaries
    top_genres = models.JSONField(null=True, blank=True)
    top_album = models.JSONField(null=True, blank=True)

    top_playlists = models.JSONField(null=True, blank=True)  # Store playlist data as a list of dictionaries
    is_public = models.BooleanField(default=True)
    spirit_animal = models.CharField(max_length=400, null=True, blank=True)

    liked_by_users = models.ManyToManyField(User, related_name='liked_wraps', blank=True)


def __str__(self):
        return f"Wrap for {self.user.email} on {self.created_at}"

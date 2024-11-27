# Generated by Django 4.2.16 on 2024-11-27 17:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Wrap",
            fields=[
                (
                    "wrap_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("title", models.CharField(default="Untitled Wrap", max_length=255)),
                ("theme", models.CharField(default="space", max_length=50)),
                ("theme_gifs", models.JSONField()),
                (
                    "time_range",
                    models.CharField(
                        choices=[
                            ("short_term", "Last 4 Weeks"),
                            ("medium_term", "Last 6 Months"),
                            ("long_term", "All Time"),
                        ],
                        default="medium_term",
                        max_length=20,
                    ),
                ),
                ("top_tracks", models.JSONField()),
                ("top_artists", models.JSONField()),
                ("top_genres", models.JSONField(blank=True, null=True)),
                ("top_album", models.JSONField(blank=True, null=True)),
                ("top_playlists", models.JSONField(blank=True, null=True)),
                ("top_suggested_songs", models.JSONField(blank=True, null=True)),
                ("is_public", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("username", models.CharField(max_length=50, unique=True)),
                ("password", models.CharField(max_length=128)),
                ("spotify_id", models.CharField(blank=True, max_length=50, null=True)),
                ("access_token", models.TextField(blank=True, null=True)),
                ("refresh_token", models.TextField(blank=True, null=True)),
                ("token_expires", models.DateTimeField(blank=True, null=True)),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
                ("last_login", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                (
                    "favorites",
                    models.ManyToManyField(
                        blank=True,
                        related_name="favorited_by_users",
                        to="Spotify_Wrapped.wrap",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="wrap",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

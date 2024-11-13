# your_app/admin.py
from django.contrib import admin
from .models import CustomUser, Wrap
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)

    # Define fieldsets to include only the fields from CustomUser
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password', 'is_active', 'is_staff', 'spotify_id', 'access_token', 'refresh_token', 'token_expires', 'date_joined', 'last_login')
        }),
    )

    # Make certain fields read-only
    readonly_fields = ('date_joined', 'last_login')

admin.site.register(CustomUser, CustomUserAdmin)

class WrapAdmin(admin.ModelAdmin):
    model = Wrap
    list_display = ('user', 'title', 'created_at', 'theme', 'time_range')
    search_fields = ('user__email', 'title')  # Enable search by user email and title
    list_filter = ('theme', 'time_range')  # Filter by theme and time range

admin.site.register(Wrap, WrapAdmin)  # Register the Wrap model with its admin class
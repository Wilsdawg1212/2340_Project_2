import requests
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

def refresh_spotify_token(user):
    # Check if the access token has expired
    if timezone.now() >= user.token_expires:
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': user.refresh_token,
                'client_id': settings.SPOTIFY_CLIENT_ID,
                'client_secret': settings.SPOTIFY_CLIENT_SECRET,
            }
        )

        token_info = response.json()
        new_access_token = token_info.get('access_token')
        expires_in = token_info.get('expires_in')  # in seconds

        # Update the user's access token and expiration time
        user.access_token = new_access_token
        user.token_expires = timezone.now() + timedelta(seconds=expires_in)
        user.save()

        return new_access_token
    return user.access_token
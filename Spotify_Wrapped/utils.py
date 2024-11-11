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

def get_top_tracks(access_token, time_range='medium_term', limit=10):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(
        'https://api.spotify.com/v1/me/top/tracks',
        headers=headers,
        params={'limit': limit, 'time_range': time_range}
    )
    data = response.json().get('items', [])
    return [
        {
            'track_name': track['name'],
            'artist_name': track['artists'][0]['name'],
            'album_name': track['album']['name'],
            'album_image_url': track['album']['images'][0]['url'],
            'track_url': track['external_urls']['spotify'],
            'duration_ms': track['duration_ms']
        }
        for track in data
    ]

def get_top_artists(access_token, time_range='medium_term', limit=10):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(
        'https://api.spotify.com/v1/me/top/artists',
        headers=headers,
        params={'limit': limit, 'time_range': time_range}
    )
    data = response.json().get('items', [])
    return [
        {
            'artist_name': artist['name'],
            'genres': artist['genres'],
            'followers': artist['followers']['total'],
            'artist_image_url': artist['images'][0]['url'],
            'artist_url': artist['external_urls']['spotify']
        }
        for artist in data
    ]

def get_top_album(top_tracks):
    if top_tracks:
        return {
            'album_name': top_tracks[0]['album_name'],
            'artist_name': top_tracks[0]['artist_name'],
            'album_image_url': top_tracks[0]['album_image_url'],
            'album_url': top_tracks[0]['track_url']
        }
    return None

def get_top_genres(top_artists):
    genre_count = {}
    for artist in top_artists:
        for genre in artist['genres']:
            genre_count[genre] = genre_count.get(genre, 0) + 1
    sorted_genres = sorted(genre_count, key=genre_count.get, reverse=True)
    return sorted_genres[:5]
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
            'duration_ms': track['duration_ms'],
            'track_id': track['id'],
            'track_uri': track['uri']
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
            'artist_url': artist['external_urls']['spotify'],
            'artist_id': artist['id']
        }
        for artist in data
    ]

def get_top_album(top_tracks):
    print(top_tracks)
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
    five_sorted_genres = sorted_genres[:5]
    five_sorted_genres.append(top_artists[0]['artist_id'])
    return five_sorted_genres

def get_top_playlists(access_token, time_range='medium_term', limit=5):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(
        'https://api.spotify.com/v1/me/playlists',
        headers=headers,
        params={'limit': limit, 'time_range': time_range}
    )
    data = response.json().get('items', [])
    return [
        {
            'playlist_name': playlist['name'],
            'owner_name': playlist['owner']['display_name'],
            'playlist_url': playlist['external_urls']['spotify'],
            'playlist_image_url': playlist['images'][0]['url'] if playlist['images'] else None,
            'track_count': playlist['tracks']['total']
        }
        for playlist in data
    ]



import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY


def get_insight_from_llm(wrap_data, question):
    # Prepare the conversation messages
    messages = [
        {"role": "system", "content": "You are an assistant that provides creative insights about music data."},
        {"role": "user", "content": f"User's Spotify data: {wrap_data}\n{question}"}
    ]

    try:
        # Use the v1/chat/completions endpoint
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use gpt-4 if needed
            messages=messages,
            max_tokens=100  # Adjust max tokens based on expected response length
        )

        # Extract the assistant's reply
        return response['choices'][0]['message']['content'].strip()

    except openai.error.OpenAIError as e:
        # Handle any API errors gracefully
        return f"Error: {e}"
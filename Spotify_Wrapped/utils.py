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
            'track_id': track['id']
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

def get_suggested_songs(access_token, time_range='medium_term', limit=5):
    """
    This function gets the top tracks, artists, and genres of a user and then
    uses this data to request song recommendations from the Spotify API.
    """

    # Step 2: Get user's top tracks, artists, and genres
    top_tracks = get_top_tracks(access_token)
    top_artists = get_top_artists(access_token)
    top_genres = get_top_genres(top_artists)
    print(top_genres)

    # Step 3: Build seed parameters using the top tracks, artists, and genres
    seeds = {}
    if top_artists:
        seeds['seed_artists'] = ','.join([artist['artist_id'] for artist in top_artists[:2]])  # Limit to top 5 artists
    if top_tracks:
        seeds['seed_tracks'] = ','.join([track['track_id'] for track in top_tracks[:2]])  # Limit to top 5 tracks

    # Step 4: Request song recommendations from Spotify API
    print(seeds)
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(
        'https://api.spotify.com/v1/recommendations',
        headers=headers,
        params={**seeds, 'limit': limit, 'market': 'US', 'time_range': time_range}  # Customize the number of recommendations and market
    )

    # Step 5: Check for errors and handle the response
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print("Response:", response.text)  # Print the response content
        return []

    data = response.json().get('tracks', [])
    return [
        {
            'track_name': track['name'],
            'artist_name': track['artists'][0]['name'],
            'album_name': track['album']['name'],
            'album_image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'track_url': track['external_urls']['spotify'],
            'duration_ms': track['duration_ms']
        }
        for track in data
    ]
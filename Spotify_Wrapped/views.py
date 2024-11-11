from django.shortcuts import render, redirect
from Spotify_Wrapped.forms import SignupForm
from Spotify_Wrapped.forms import LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import requests
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .utils import refresh_spotify_token
from django.contrib.auth import logout

# all the view functions

def logout_view(request):
    logout(request)  # Logs out the user
    return redirect('index')
def spotify_auth(request):
    scope = 'user-top-read user-library-read'  # or any scopes you need for your app

    auth_url = (
        f"https://accounts.spotify.com/authorize?"
        f"client_id={settings.SPOTIFY_CLIENT_ID}&response_type=code"
        f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}&scope={scope}"
        f"&show_dialog=true"
    )
    return redirect(auth_url)

def link_spotify(request):
    if request.method == 'POST':
        return redirect('spotify_auth')  # When the user clicks the button, start the OAuth flow
    return render(request, 'Spotify_Wrapped/link_spotify.html')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('dashboard')  # Route them to link their Spotify account
    else:
        form = SignupForm()
    return render(request, 'Spotify_Wrapped/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect directly to the dashboard
            else:
                form.add_error(None, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'Spotify_Wrapped/login.html', {'form': form})

def index(request):
    return render(request, 'Spotify_Wrapped/index.html')

@login_required(login_url='index')
def dashboard(request):
    user = request.user

    return render(request, 'Spotify_Wrapped/dashboard.html', {
        'user': user,
    })

# def check_account(request):
#     user = request.user
#     # Refresh the token if necessary
#     access_token = refresh_spotify_token(user)
#
#     # Use the access token to make API requests if needed (optional)
#     headers = {
#         'Authorization': f'Bearer {access_token}'
#     }
#     spotify_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
#
#     # Render the dashboard and pass Spotify data to the template
#     return render(request, 'Spotify_Wrapped/dashboard.html', {
#         'user': user,
#         'spotify_data': spotify_response.json()
#     })

def spotify_callback(request):
    # Check if there's an authorization code in the request (from Spotify OAuth)
    code = request.GET.get('code')

    if code:
        # Exchange the code for an access token and refresh token
        token_info = exchange_code_for_tokens(code)

        # Extract tokens and token expiration
        access_token = token_info.get('access_token')
        refresh_token = token_info.get('refresh_token')
        expires_in = token_info.get('expires_in')  # in seconds
        token_expires = timezone.now() + timedelta(seconds=expires_in)

        # Get Spotify user information
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        user_info_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        user_info = user_info_response.json()
        spotify_id = user_info.get('id')  # Spotify user ID

        # Update the custom user model with the Spotify data
        user = request.user
        user.spotify_id = spotify_id
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.token_expires = token_expires
        user.save()

        # Redirect to the dashboard after handling Spotify data
        return redirect('dashboard')

    else:
        return redirect('login')

def exchange_code_for_tokens(code):
    # Exchange the authorization code for an access token and refresh token
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
            'client_id': settings.SPOTIFY_CLIENT_ID,
            'client_secret': settings.SPOTIFY_CLIENT_SECRET,
        }
    )

    return response.json()

def error_page(request):
    return render(request, 'Spotify_Wrapped/link_error.html')

def top_tracks(request):
    user = request.user
    access_token = refresh_spotify_token(user)

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    try:
        response = requests.get(
            'https://api.spotify.com/v1/me/top/tracks',
            headers=headers,
            params={
                'limit': 5,
                'time_range': 'long_term'
            }
        )
    except requests.exceptions.RequestException as e:
        print(f"Error fetching top tracks from Spotify: {e}")
        return [{"name": "Error fetching top tracks from Spotify.", "image": None}]

    if response.status_code == 200:
        try:
            top_tracks = response.json().get('items', [])
            track_data = [
                {
                    "name": track.get('name'),
                    "album_image": track.get('album', {}).get('images', [{}])[0].get('url')
                }
                for track in top_tracks[:5]
            ]
            while len(track_data) < 5:
                track_data.append({"name": "No additional track data found.", "album_image": None})
        except (ValueError, KeyError):
            track_data = [{"name": "Error processing top track data.", "album_image": None}]
    else:
        track_data = [{"name": f"Spotify API error: {response.status_code}", "album_image": None}]
    return track_data


# Create your views here.
def top_artists(request):
    user = request.user
    access_token = refresh_spotify_token(user)

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    try:
        response = requests.get(
            'https://api.spotify.com/v1/me/top/artists',
            headers=headers,
            params={
                'limit': 5,
                'time_range': 'long_term'
            }
        )
    except requests.exceptions.RequestException as e:
        print(f"Error fetching top artist from Spotify: {e}")
        return [{"name": "Error fetching top artist from Spotify.", "image": None}]

    if response.status_code == 200:
        try:
            top_artists = response.json().get('items', [])
            artist_data = [
                {"name": artist.get('name'), "image": artist.get('images', [{}])[0].get('url')}
                for artist in top_artists[:5]
            ]
            while len(artist_data) < 5:
                artist_data.append({"name": "No additional artist data found.", "image": None})
        except (ValueError, KeyError):
            artist_data = [{"name": "Error processing top artist data.", "image": None}]
    else:
        artist_data = [{"name": f"Spotify API error: {response.status_code}", "image": None}]

    return artist_data


@login_required(login_url='index')
def wrapped(request):
        top_5_artist_dic = top_artists(request)
        top_5_artist_list = []
        top_5_artist_image = []
        for artist in top_5_artist_dic:
            top_5_artist_list.append(artist['name'])
        for artist_image in top_5_artist_dic:
            top_5_artist_image.append(artist_image['image'])
        artist_image_pairs = list(zip(top_5_artist_list, top_5_artist_image))

        top_5_tracks_dic = top_tracks(request)
        top_5_tracks_list = []
        top_5_tracks_image = []
        for track in top_5_tracks_dic:
            top_5_tracks_list.append(track['name'])
        for track_image in top_5_tracks_dic:
            top_5_tracks_image.append(track_image['album_image'])
        track_image_pairs = list(zip(top_5_tracks_list, top_5_tracks_image))
        print(artist_image_pairs)
        print(track_image_pairs)
        return render(request, 'Spotify_Wrapped/wrapped.html', {
         'artist_image_pairs': artist_image_pairs,
         'track_image_pairs': track_image_pairs,
    })

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
            print(f"Email: {email}")  # Debugging print statement
            print(f"Password: {password}")  # Debugging print statement

            user = authenticate(request, email=email, password=password)
            if user is not None:
                print("Authentication successful")  # Debugging print statement
                login(request, user)
                return redirect('dashboard')  # Redirect to the dashboard
            else:
                print("Authentication failed")  # Debugging print statement
                form.add_error(None, 'Invalid email or password.')
        else:
            print("Form is not valid")  # Debugging print statement
            print(form.errors)  # Print form errors
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

def contact_dev(request):
    return render(request, 'Spotify_Wrapped/contact_dev.html')

from .models import Wrap

def title_wrap(request):
    return render(request, 'Spotify_Wrapped/title-wrap.html')

@login_required
def create_wrap(request):
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        time_range = request.POST.get('time_range', 'medium_term')
        theme = request.POST.get('theme', 'dark')

        # Get the user's Spotify access token from their session or database
        access_token = refresh_spotify_token(request.user)

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # Fetch top tracks with the specified time range
        top_tracks_response = requests.get(
            'https://api.spotify.com/v1/me/top/tracks',
            headers=headers,
            params={'limit': 10, 'time_range': time_range}
        )
        top_tracks_data = top_tracks_response.json().get('items', [])

        # Fetch top artists with the specified time range
        top_artists_response = requests.get(
            'https://api.spotify.com/v1/me/top/artists',
            headers=headers,
            params={'limit': 10, 'time_range': time_range}
        )
        top_artists_data = top_artists_response.json().get('items', [])

        # Structure the data
        top_tracks = [
            {
                'track_name': track['name'],
                'artist_name': track['artists'][0]['name'],
                'album_name': track['album']['name'],
                'album_image_url': track['album']['images'][0]['url'],
                'track_url': track['external_urls']['spotify'],
                'duration_ms': track['duration_ms']
            }
            for track in top_tracks_data
        ]

        top_artists = [
            {
                'artist_name': artist['name'],
                'genres': artist['genres'],
                'followers': artist['followers']['total'],
                'artist_image_url': artist['images'][0]['url'],
                'artist_url': artist['external_urls']['spotify']
            }
            for artist in top_artists_data
        ]

        # Create a new Wrap entry with the new fields
        Wrap.objects.create(
            user=request.user,
            title=title,
            theme=theme,
            time_range=time_range,
            top_tracks=top_tracks,
            top_artists=top_artists
        )

        return render(request, 'Spotify_Wrapped/generate.html', {
            'title': title,
            'theme': theme,
            'time_range': time_range,
            'top_tracks': top_tracks,
            'top_artists': top_artists
        })

    # If the request method is not POST, render the form
    return render(request, 'Spotify_Wrapped/generate.html')



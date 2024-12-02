import json

from django.shortcuts import render, get_object_or_404
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
from django import forms
from django.contrib import messages

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

class LogInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

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
                print("Authentication failed")  # Debugging print statement
                form.add_error(None, 'Invalid email or password.')
        else:
            print("Form errors:", form.errors)
    else:
        form = LoginForm()
    return render(request, 'Spotify_Wrapped/login.html', {'form': form})

def index(request):
    return render(request, 'Spotify_Wrapped/index.html')

@login_required(login_url='index')
def dashboard(request):
    user = request.user

    wraps = Wrap.objects.filter(user=request.user)
    return render(request, 'Spotify_Wrapped/dashboard.html', {
        'user': user,
        'wraps': wraps
    })

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
    user = request.user
    if not user.spotify_id:
        messages.error(request, "You need to link your Spotify account to create a wrap.")
        return redirect(request.META.get('HTTP_REFERER', '/default-url/'))
    return render(request, 'Spotify_Wrapped/title-wrap.html')

THEME_GIFS = {
    'space': [
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExamtyem02c211NDUyam95dmt1ZGliNjF0b2k3YndrajZuaWtneHh3byZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/kiWlpxD6hXmvTL8dio/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExenZmNTR1YTA2eXpuZHpkOWtoM2FmYnFibm5xYTNrZTFhdTM2dTZnMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o6EhNwxVvOYkfwhyg/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3d2N2RiNDF6cGY2dTdzcGRyZzZ2ZmtycjdpaHNlZDVuNTE2dnJiMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oEduRygZtVxloohws/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWdhZG9jMDhqNHJvaW1kY3RhY290Znc4NjlvMDl2N29hdm1pNGgwaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Fbox1ygIqnga5dLinz/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExdHR2Zjhua2dvZ3FrZG5zbGdiMm44d2oyOTBwN3N6ZDlpZ3l3c2ZpdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPtjElfqwMOTbH2/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzhrOGR1dHR5Mjc4NnF1azA2bTJhbmRtdjBoMGVoaW94N2hxYmdtdSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jXuOAS4Bv7LX10xYyc/giphy-downsized-large.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTg2cDFwc2VyMXV4eXZiMHE1Y3Fia2Nuc2Z5cW8xcGtsOHc0YjdidiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT8qBhrlNooHBYR9f2/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExejVoY2p3bTlzYW11ZW16bDZpeG50dWxlN2J4em50c213Y3VlcTJqNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/YqhIK6Gbor6CLeloBq/giphy-downsized-large.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHp4ejZhY25obzdlMmQydjU5ZG5ndnY3ZGN3M2RvMTgxN3dvY2syZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7buijTqhjxjbEqjK/giphy.gif',
    ],
    'christmas': [
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExbzV0d3NtbnhsdTI4cHN2ZjA2b2FkbzV3NWg2bXllcDNnMmhyajFsZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oz8xRF8doADfuvCvu/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWd4Y3J1M2Yzc3Jsa2VyY2NvYXpxbm1zZnBudnd3NW11a25oYzlmeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/11BEQyXROgnLTG/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcHFjamhxMmplaGZmZWJnbzN3czVwenBkdWd1Yjl1cWo0OWFiZDR1aiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XXvnnrJJnOVl6/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjM3MXF3dGltYWJvc3pobG55Y25lYzRhajBoNGpzcXZobTgzM2ttMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/K90ckojkohXfW/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExOTdmZndhNWR4eXJ4Z2pxcmNyM2MycWg1ejMyMDN1YTNrdWQ5djB4byZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/pxIEIhFkA4htatDUaj/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYW54ZWZ0NWl2cDdqMmV2aDY3N2RhbTU2OHI4NWg5dDJtZGVvYTE1bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/wPn31WOCzkvKg/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHB2NnpraWlud21ibG41cDZycmUxbHo1Z3k4cGJpdDQxNXhncWlrdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/24Io5qtKoonPa/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGJ1ZWJ1YmFvdGNhY203Y3M0Ymx4OXZ1ZmVpYzZmdDMyOW8yN2RzZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l3q2yNwWQMv6YHABi/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExczR0dWlpN2NpMnF4MG90ZWM1MnVmNnRwYThhbWplc24wZGdzY3JtbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/nJ0kvaGWPwtl6/giphy.gif',
    ],
    'valentine': [
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYmZvanZmb3VkOWN5cWwzZ3BoN2kwaDJ5cHhkMmZveXo5aThvNWc2cCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKoWXm3okO1kgHC/giphy-downsized-large.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDRhcDhjbTJwc3dmMHhmY3MxcTA0OGNkejR4NHpubzNta3hlbXNuaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26BRv0ThflsHCqDrG/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNmNiODJqZ3Z6MDVrbHl0eDVja2Iyc3Z6NTBsNW55a21sdGRqN2g1diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ySHDW1uSwYMeqPd2gX/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3dramw5a3Ixdm9vemZ4YnRtcXJnNWtvaWtwaGdkcG5rcmF3NGNuaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/TmngSmlDjzJfO/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExajN4N3F1ZDkwbTZ2eG83cHh0eXFoN3FmbDR3bHdwcTFkMWltcXUyZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oz8xGRXaIHGqts3hC/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExODAxZnJjNWc5ZGtieTg1NmpyNXJ1YTV6ZjV1cWN5eDF1eTlxZTdzZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/11fIOE3vkIPdIY/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExeXF1YXpncGtpMjZraWtjeGd3ZzBocjNpc2gzZGZibmsxc3EyNXB3ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/EUgI9BSalN3mo/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcXpkcHVpbG9qYWlhbHB0aWVteGwyeXN4OTE1c2ZweXhpNDZ3ZDJpMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9dg/2FxwhwSseOqrxqYKfM/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExeDI1MHM3Y2tja3VuM2hybHIyYjVvZm9xejlmNGRuNHRwYTl6NXFtOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/h1P26E2bQuE80/giphy.gif',
    ],
    'halloween': [
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExaW80ZWlpMmYzYXFya3NoZ3NlbDBrNGx6Mm8yMWt3amlvZDhocDU3NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l41lOhiLU8aYsRxyE/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmV4NGRlamtwNHE1dHRwc3VpeHBvMzhrcnJrbXNmMnJyYThlNnlmMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26n7bmOQtVVPXxc7m/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDBmbjdmaHJncGR4MXZ6N3U1Y3B2MGw2c2pjdXcwd28wOG02M3ZyNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/46rC1DxQPSDFTg07n8/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExa29uMTdjbm5sYnNwbXFlOGptdnRqNXE0eGJvYWVnanduMDF3OWFzdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/c1IChgTRCPRs5sOLEb/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3dndjkxZXhlbzk4Yndvb2w4M2NmZHl0M25xdjAyOTVrejJyaWM1YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/UYGS53pznEblK/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGdiejRqNnVyOTA4Z2M4aWNwcDJvN2wxejRqaGphZ3RvaTdwczk0YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cImkU4DZjyUqm6fBMq/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExenhmeW0zMG9rdmtkbjFhdm81anRtYnRzd3BkaTQ4ZjAxdm9zb25zZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fdPrj2ik6DYjL3gOv4/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXo1MndvbjZqZW5rNGg2YXR5ZzNoanVkbnhneWVhNG9weHp0Y2pyOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/rAbKGNGM99DBC/giphy.gif',
        'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYzNpdDFlNWlhdDF6MDQ4c25xdXh3NHh4bGQ0bmVpN2pvcGxjOHI4aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1veHAi4orHzSMMFPBt/giphy.gif',
    ]
}

from .utils import get_top_tracks, get_top_artists, get_top_album, get_top_genres, get_top_playlists, get_suggested_songs
from .utils import get_top_tracks, get_top_artists, get_top_album, get_top_genres, get_top_playlists, get_suggested_songs, get_insight_from_llm
@login_required
def create_wrap(request):
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        time_range = request.POST.get('time_range', 'medium_term')
        theme = request.POST.get('theme', 'space')
        is_public = request.POST.get('is_public') == 'true'  # Convert string to boolean

        theme_gifs = THEME_GIFS.get(theme, THEME_GIFS['space'])
        print("Hello world 1")
        print(time_range)

        # Get the user's Spotify access token
        access_token = refresh_spotify_token(request.user)

        # Retrieve data using helper functions
        top_tracks = get_top_tracks(access_token, time_range)
        top_artists = get_top_artists(access_token, time_range)
        top_album = get_top_album(top_tracks)
        top_genres = get_top_genres(top_artists)
        top_playlists = get_top_playlists(access_token, time_range)
        top_suggested_songs = get_suggested_songs(access_token, time_range)
        track_uris = [track['track_uri'] for track in top_tracks]

        # Prepare data for the LLM prompt
        wrap_data = {
            "top_tracks": top_tracks,
            "top_artists": top_artists,
            "top_genres": top_genres,
            "top_album": top_album,
        }
        question = "Based on this user's Spotify data, what is their spirit animal?"

        # Call the LLM for the spirit animal
        spirit_animal = get_insight_from_llm(wrap_data, question)[:255]
        print(f"Generated spirit animal: {spirit_animal}")

        # Create a new Wrap entry
        Wrap.objects.create(
            user=request.user,
            title=title,
            theme=theme,
            theme_gifs=theme_gifs,
            time_range=time_range,
            is_public=is_public,  # Save the visibility (public/private)
            top_tracks=top_tracks,
            top_artists=top_artists,
            top_genres=top_genres,
            top_album=top_album,
            top_playlists=top_playlists,
            top_suggested_songs=top_suggested_songs,
            spirit_animal=spirit_animal,
        )
        print('_____________________TOP TRACKS _________________________')
        print(top_tracks)
        print('_____________________TOP ARTISTS _________________________')
        print(top_artists)
        print('_____________________TOP ALBUM _________________________')
        print(top_album)
        print('_____________________TOP SUGGESTED _________________________')
        print(top_suggested_songs)
        print('_____________________TOP TRACKS URIs _________________________')
        print(track_uris)
        for i in range(len(track_uris)):
            track_uris[i] = track_uris[i][14:]
        print(track_uris)



        return render(request, 'Spotify_Wrapped/wrapped.html', {
            'title': title,
            'theme': theme,
            'theme_gifs': theme_gifs,
            'time_range': time_range,
            'top_tracks': top_tracks,
            'top_artists': top_artists,
            'top_genres': top_genres,
            'top_album': top_album,
            'top_playlists': top_playlists,
            'top_suggested_songs': top_suggested_songs,
            'spotify_access_token': access_token,
            'track_uris': track_uris,
            'spirit_animal': spirit_animal,
        })

    # If the request method is not POST, render the form
    print("Hello world 4")
    return render(request, 'Spotify_Wrapped/title-wrap.html')


def feed_view(request):
    wraps = Wrap.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'Spotify_Wrapped/feed.html', context={'wraps': wraps})


def wrap_detail(request, wrap_id):
    # Get the wrap from the database
    wrap = get_object_or_404(Wrap, wrap_id=wrap_id, user=request.user)
    print("Theme gifs test below")
    print(wrap.theme_gifs)

    # Render the template with the wrap data
    return render(request, 'Spotify_Wrapped/wrapped.html', {
        'wrap': wrap,
        'wrap_id': wrap.wrap_id,
        'title': wrap.title,
        'theme': wrap.theme,
        'theme_gifs': wrap.theme_gifs,
        'time_range': wrap.get_time_range_display(),
        'top_tracks': wrap.top_tracks,
        'top_artists': wrap.top_artists,
        'top_genres': wrap.top_genres,
        'top_album': wrap.top_album,
        'top_playlists': wrap.top_playlists,
        'top_suggested_songs': wrap.top_suggested_songs,
    })


@login_required
def update_visibility(request, wrap_id):
    wrap = get_object_or_404(Wrap, wrap_id=wrap_id, user=request.user)
    if request.method == "POST":
        is_public = request.POST.get("is_public") == "true"
        wrap.is_public = is_public
        wrap.save()

    # Render the same page with updated wrap data
    return render(request, 'Spotify_Wrapped/wrapped.html', {'wrap': wrap})

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

@login_required
@csrf_exempt
def toggle_favorite(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            wrap_id = data.get("wrap_id")

            # Fetch the wrap object
            wrap = Wrap.objects.get(wrap_id=wrap_id)
            user = request.user

            # Debugging: Print data
            print(f"User: {user.email}, Wrap: {wrap.title}")

            # Toggle the like status
            if user in wrap.liked_by_users.all():
                wrap.liked_by_users.remove(user)
                is_liked = False
            else:
                wrap.liked_by_users.add(user)
                is_liked = True

            # Debugging: Print the result
            print(f"Is Liked: {is_liked}, Likes Count: {wrap.liked_by_users.count()}")

            # Return the updated count and status
            return JsonResponse({
                "success": True,
                "is_liked": is_liked,
                "likes_count": wrap.liked_by_users.count()
            })
        except Wrap.DoesNotExist:
            print("Wrap not found.")
            return JsonResponse({"success": False, "message": "Wrap not found."}, status=404)
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    print("Invalid request method.")
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)


@login_required
def feed_filtered(request):
    print("feed view called")
    wraps = Wrap.objects.all()  # Default: show all wraps

    if request.method == "POST":
        # Get the checkbox value (will be 'on' if checked)
        show_favorites = request.POST.get('show_favorites') == 'on'

        if show_favorites:
            # Filter wraps that the user has liked
            wraps = Wrap.objects.filter(liked_by_users=request.user)
            print("Filtered favorites")

    print(wraps)
    return render(request, 'Spotify_Wrapped/feed.html', {'wraps': wraps})


@login_required
def delete_wrap(request, wrap_id):
    """Deletes a user's wrap."""
    wrap = get_object_or_404(Wrap, wrap_id=wrap_id)

    # Ensure that the current user is the one who created the wrap
    if wrap.user == request.user:
        wrap.delete()
        messages.success(request, "Your wrap has been successfully deleted.")
    else:
        messages.error(request, "You can only delete your own wraps.")

    return redirect('dashboard')  # Redirect back to the dashboard

@login_required
def settings(request):
    return render(request, 'Spotify_Wrapped/settings.html')

def delete_account(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        user.delete()  # Deletes the user from the database
        logout(request)  # Logs the user out
        return JsonResponse({'success': True, 'message': 'Account deleted successfully.'})
    return JsonResponse({'success': False, 'message': 'Unauthorized request.'}, status=403)
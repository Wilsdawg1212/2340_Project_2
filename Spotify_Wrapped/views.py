from django.shortcuts import render, redirect
from Spotify_Wrapped.forms import SignupForm
from Spotify_Wrapped.forms import LoginForm
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.conf import settings

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
            return redirect('link_account')  # Route them to link their Spotify account
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

def dashboard(request):
    return render(request, 'Spotify_Wrapped/dashboard.html')

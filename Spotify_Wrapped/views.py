from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def wrapped(request):
    return render(request, 'Spotify_Wrapped/wrapped.html')

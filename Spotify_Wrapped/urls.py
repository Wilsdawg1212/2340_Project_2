from django.urls import path
from Spotify_Wrapped import views

urlpatterns = [
    path('', views.index, name='index'),
]
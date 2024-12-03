from django.urls import path
from Spotify_Wrapped import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),  # Signup form
    path('login/', views.login_view, name='login'),  # Login form
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard after login/signup
    path('link_account/', views.link_spotify, name='link_account'),
    # path('logout/', views.logout_view, name='logout'),  # Logout view
    path('spotify-auth/', views.spotify_auth, name='spotify_auth'), # Spotify OAuth
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('link_error/', views.error_page, name='error_page'),
    path('logout/', views.logout_view, name='logout'),
    path('contact_dev/', views.contact_dev, name='contact_dev'),
    path('title_wrap/', views.title_wrap, name='title_wrap'),
    path('generate_wrap/', views.create_wrap, name='generate_wrap'),
    path('feed/', views.feed_view, name='feed'),
    path('wrap/<uuid:wrap_id>/', views.wrap_detail, name='wrap_detail'),
    path("wrap/<uuid:wrap_id>/update-visibility/", views.update_visibility, name="update_visibility"),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path("feed_filtered/", views.feed_filtered, name='feed_filtered'),
    path('delete_wrap/<uuid:wrap_id>/', views.delete_wrap, name='delete_wrap'),
    path('settings/', views.delete_account_page, name='settings'),
    path('delete_account/', views.delete_account, name='delete_account'),
]
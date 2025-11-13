from django.urls import path

from . import views

urlpatterns = [
    path("", views.active_listings, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.create_listing , name='create_listing'),
    path("index/<int:id>/<str:title>", views.individual_listing, name='individual_listing'),
    path('closed', views.closed_listings, name='closed'),
    path('togglewatchlist/<int:id>/<str:title>', views.toggle_watchlist, name='toggle'),
    path('watchlist', views.watchlist, name='user_watchlist'),
    path("categories", views.category, name='category'),
    path("categories/<str:title>", views.category, name='category-item')
]

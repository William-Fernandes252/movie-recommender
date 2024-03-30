from django.urls import path

from . import views

urlpatterns = [
    path("", views.MovieListView.as_view(), name="movie-list"),
    path("<int:pk>/", views.MovieDetailView.as_view(), name="movie-detail"),
    path("infinite/", views.MovieInfiniteRatingView.as_view(), name="movie-infinite"),
    path("popular/", views.MovieListView.as_view(), name="movie-popular"),
]

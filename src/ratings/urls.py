from django.urls import path

from . import views

urlpatterns = [path("", views.rate_movie, name="rate-movie")]

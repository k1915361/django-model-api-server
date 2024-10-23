from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views


app_name = 'polls'
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("logged-in/", views.logged_in_view, name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("logout/", views.logout_view, name="logout"),
]

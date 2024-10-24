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
    path("login-view/", views.authentication_view, name="login-view"),
    path("loginn/", views.check_authentication, name="loginn"),
    path("process-model-options/", views.process_model_options_view, name="process model options"),
    path("human-reinforced-feedback/", views.human_reinforced_feedback_view, name="human reinforced feedback view"),
    path("final-task-analytics/", views.final_task_analytics_view, name="final task analytics"),
    path("previous-tasks/", views.previous_tasks_view, name="previous tasks"),
    path("personal-model-repo/", views.personal_model_repo_view, name="personal model repo"),
    path("personal-dataset-repo/", views.personal_dataset_repo_view, name="personal dataset repo"),
    path("personal-dataset-analysis/", views.personal_dataset_analysis_view, name="personal dataset analysis"),
]

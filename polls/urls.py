from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from . import api

app_name = 'polls'
urlpatterns = [
    path("", views.index_homepage_view, name="index"),
    path("search-dataset-name", views.search_dataset_name_view, name="search dataset name"),
    path("home/", views.index_homepage_view, name="index"),
    path("profile/", views.profile_view, name="profile"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("logout/", views.logout_view, name="logout"),
    path("login-view/", views.login_view, name="login view"),
    path("login-retry-view/", views.login_retry_view, name="login retry view"),
    path("login-view/login/", views.login_user, name="login"),
    path("login-retry-view/login/", views.login_user, name="retry login"),
    path("register-view/", views.register_view, name="register view"),
    path("register-retry-view/", views.register_retry_view, name="register retry view"),
    path("register-view/register/", views.register, name="register"),
    path("register-retry-view/register/", views.register, name="register retry "),
    path("upload-model/", views.upload_model, name="upload model form"),
    path("upload-folder/", views.upload_folder_view, name="upload folder view"),
    path("public-dataset-list-view/", views.public_dataset_list_view, name="public dataset list view"),
    path("public-model-list-view/", views.public_model_list_view, name="public model list view"),
    path("dataset-list-view-to-fork/", views.model_list_view_to_fork, name="dataset list view to fork"),
    path("public-dataset-data-view:<int:pk>/", views.public_dataset_list_view, name="public-dataset-data-view"),
    path("private-dataset-list-view/", views.private_dataset_list_view, name="private-dataset-list-view"),
    path("private-model-list-view/", views.private_model_list_view, name="private-model-list-view"),
    path("user_dataset_list_path_view/", views.user_dataset_list_path_view, name="user_dataset_list_path_view"),
    path("process-model-options/", views.process_model_options_view, name="process model options"),
    path("human-reinforced-feedback/", views.human_reinforced_feedback_view, name="human reinforced feedback view"),
    path("final-task-analytics/", views.final_task_analytics_view, name="final task analytics"),
    path("previous-tasks/", views.previous_tasks_view, name="previous tasks"),
    path("personal-model-repo/", views.personal_model_repo_view, name="personal model repo"),
    path("personal-dataset-repo/", views.personal_dataset_repo_view, name="personal dataset repo"),
    path("personal-dataset-analysis/", views.personal_dataset_analysis_view, name="personal dataset analysis"),
    path("model-list-choose-one-to-relate-dataset/", views.model_list_choose_one_to_relate_a_dataset,
        name="model_list_choose_one_to_relate_dataset"),
    
    path("login-api/", views.login_api, name="login api"),
    path("models/", api.get_models_api, name="get models api"),    
    path("datasets/", api.get_datasets_api, name="get datasets api"),
    path('models_/', api.ModelList.as_view()),
    path('datasets_/', api.DatasetList.as_view()),
    path('users/', api.UserList.as_view()),
    path('models_/<int:pk>/', api.ModelDetail.as_view()),
    path('users/<int:pk>/', api.UserDetail.as_view()),
    path('datasets_/<int:pk>/', api.DatasetDetail.as_view()),
    path('test_list_random_values/', api.test_list_random_values),
    path('test_get_with_token_authorisation/', api.test_get_with_token_authorisation),
    path('model_form_post/', api.model_form_post),    
]

urlpatterns = format_suffix_patterns(urlpatterns)

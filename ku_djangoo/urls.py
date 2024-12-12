"""
URL configuration for ku_djangoo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

from tutorial.quickstart import views as serializer_views

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView, 
    TokenVerifyView
)

from polls import api

router = routers.DefaultRouter()
router.register(r'users', serializer_views.UserViewSet)
router.register(r'groups', serializer_views.GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/verify/protected-data/', api.ProtectedDataView.as_view(), name='ProtectedDataView'),
    path('api/token/login/cookie/', api.CustomLoginTokenAccessView.as_view(), name='CustomLoginTokenAccessView'),
    path('api/token/refresh/cookie/', api.CustomTokenRefreshView.as_view(), name='CustomTokenRefreshView'),
    path('api/token/test/login/cookie/', api.TestUserInfoAndCookie.as_view(), name='TestUserInfoAndCookie'),
    path('api/top-models/', api.model_list_user, name='model_list_user'),
    path('api/top-datasets/', api.dataset_list_user, name='dataset_list_user'),
    path('api/login/check/', api.user_login_check, name='user_login_check'),
    path('api/user/', api.user_profile, name='user_profile'),
    path('api/user/models/', api.user_private_models, name='user_private_models'),
    path('api/user/datasets/', api.user_private_datasets, name='user_private_datasets'),
    path('api/user/models/page/', api.user_and_public_models_pages, name='user_and_public_models_pages'),
    path('api/user/datasets/page/', api.user_and_public_datasets_pages, name='user_and_public_datasets_pages'),
    path('api/test/', api.test_api, name='test_api'),    
    path('api/model/search/', api.search_model_by_name, name='search_model_by_name'),    
    path('api/model/upload/', api.model_form_post),
    path('api/dataset/upload/', api.dataset_form_post),
    path('api/dataset/<int:id>/', api.DatasetDetail.as_view()),
    path('api/dataset/download/<int:id>/', api.download_dataset_zip),
    path('api/dataset/download/test/', api.test_download_dataset_zip),
    path('api/datasets/page/test/', api.test_page_range),
    path('api/model/download/<int:id>/', api.download_model_zip),
    path('api/model/<int:id>/', api.ModelDetail.as_view()),

    path('api/me/username/', api.get_request_username, name=''),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('polls/', include('polls.urls', namespace='polls')),
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("change-password/", auth_views.PasswordChangeView.as_view()),
    path("accounts/djangoo-login/", auth_views.LoginView.as_view(template_name="ku_djangoo/login_djangoo.html")),
    path("accounts/djangoo-profile/", auth_views.LoginView.as_view(template_name="ku_djangoo/login_djangoo.html")),
]
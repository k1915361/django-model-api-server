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
from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views

from tutorial.quickstart import views as serializer_views

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView, 
    TokenVerifyView
)

from polls import api
from ku_djangoo import asgi

from django.conf import settings
from django.conf.urls.static import static

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
    path('api/token/access/', api.AccessJWToken.as_view()),
    path('api/token/csrf/', api.get_csrf_token),
    path('api/token/csrf/test/', api.get_csrf_token_test),
    
    path('api/signup/', api.signup, name='SignUpAPI'),

    path('api/token/logout/cookie/', api.CustomLogoutTokenView.as_view(), name='CustomLogoutTokenView'),    
    path('api/token/check-login/cookie/', api.CustomCheckLoginStateTokenView.as_view(), name='CustomCheckLoginTokenView'),        
    path('api/token/refresh/cookie/', api.CustomTokenRefreshView.as_view(), name='CustomTokenRefreshView'),
    path('api/token/test/login/cookie/', api.TestUserInfoAndCookie.as_view(), name='TestUserInfoAndCookie'),
    path('api/top-models/', api.model_list_user, name='model_list_user'),
    path('api/top-datasets/', api.dataset_list_user, name='dataset_list_user'),
    path('api/login/check/', api.user_login_check, name='user_login_check'),
    path('api/user/', api.user_profile, name='user_profile'),
    path('api/user/models/', api.user_models, name='user_models'),
    path('api/user/private/models/', api.user_private_models, name='user_private_models'),
    path('api/user/models/page/', api.user_and_public_models_pages, name='user_and_public_models_pages'),
    path('api/user/private/datasets/', api.user_private_datasets_api, name='user_private_datasets'),
    path('api/user/datasets/', api.user_datasets_api, name='user_datasets'),
    path('api/user/datasets/page/', api.user_and_public_datasets_pages, name='user_and_public_datasets_pages'),
    path('api/test/', api.test_api, name='test_api'),    
    path('api/model/search/', api.search_model_by_name, name='search_model_by_name'),    
    path('api/model/upload/', api.model_form_post),
    path('api/dataset/upload/', api.dataset_form_post),
    path('api/dataset/fork/', api.fork_dataset_api),
    path('api/model/fork/', api.fork_model_api),
    path('api/model-dataset/relate/', api.relate_a_model_dataset),
    path('api/dataset/<int:id>/', api.DatasetDetail.as_view()),
    path('api/dataset/download/<int:id>/', api.download_dataset_zip),
    path('api/dataset/download/test/', api.test_download_dataset_zip),
    path('api/datasets/page/test/', api.test_page_range),
    path('api/datasets/page/', api.datasets_page_range),
    path('api/models/page/', api.models_page_range),
    path('api/model/download/<int:id>/', api.download_model_zip),
    path('api/model/<int:id>/', api.ModelDetail.as_view()),
    path('api/dataset/image/test-async-stream/', asgi.test_async_stream_view),
    path('api/dataset/image/test-async-file-stream/', asgi.test_async_file_streaming),
    path("api/dataset/blob/<int:user_id>/<str:dataset_name>/<path:image_path>/",
        api.get_dataset_image, name="get_dataset_image_api",
    ),
    path("api/model/blob/<int:user_id>/<str:model_name>/<path:image_path>/",
        api.get_model_image, name="get_model_image_api",
    ),
    path('api/dataset/blob/<int:user_id>/<str:dataset_name>/<path:path>/', 
        api.respond_dataset_file_tree, name="get dataset file"
    ),
    path('api/model/blob/<int:user_id>/<str:model_name>/<path:path>/', 
        api.respond_model_file_tree, name="get model file"
    ),
    path('api/dataset/tree/<int:user_id>/<str:dataset_name>/<path:path>/', 
        api.respond_dataset_file_tree, name="get dataset file tree"
    ),
    path('api/model/tree/<int:user_id>/<str:model_name>/<path:path>/', 
        api.respond_model_file_tree, name="get model file tree"
    ),
    path('api/dataset/tree/<int:user_id>/<str:dataset_name>/', 
        api.respond_dataset_file_tree, name="get dataset file tree"
    ),
    path('api/model/tree/<int:user_id>/<str:model_name>/', 
        api.respond_model_file_tree, name="get model file tree"
    ),
    re_path(r'api/dataset/.*\.csv$', api.get_csv_data, name='csv_view'), 
    path('api/dataset/save-minio/test/', api.save_dataset_file_to_minio_api),
    path('api/dataset/minio/<int:id>/', api.read_dataset_from_minio),
    path('api/dataset/minio/<int:id>/', api.delete_dataset_file_from_minio),
    path('api/dataset/minio/<int:id>/', api.update_dataset_file_in_minio),
    path('api/dataset/minio/test/', api.read_file_from_minio_test),
    path('api/dataset/get-minio/test/zip/', api.test_get_zip_file_from_minio),
    path('api/dataset/minio/test/list/', api.list_minio_bucket_object),
    path('api/dataset/minio/temp/', api.temp),
    path('api/task/', api.create_and_get_task_id),

    path('api/me/username/', api.get_request_username, name=''),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('polls/', include('polls.urls', namespace='polls')),
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("change-password/", auth_views.PasswordChangeView.as_view()),
    path("accounts/djangoo-login/", auth_views.LoginView.as_view(template_name="ku_djangoo/login_djangoo.html")),
    path("accounts/djangoo-profile/", auth_views.LoginView.as_view(template_name="ku_djangoo/login_djangoo.html")),
]

# if settings.DEBUG:

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[1])

# Above is for Development. For Production, for GET requests, serve static files by a web server like Nginx for better performance and security.
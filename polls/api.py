from django.db.models import Q
from django.db.models import F
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, FileResponse, HttpResponse
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import (
    api_view, 
    authentication_classes, 
    permission_classes
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Dataset, Model, ModelDataset
from .views import (
    MARKDOWN_FENCED_CODE,
    handle_extract_zip_file, 
    save_model_folder_info_to_database, 
    save_dataset_to_database, 
    search_and_get_readme_markdown_by_directory,
    fork_model,
    fork_dataset
)
import re
import csv
import json
import uuid
import os 
import random
import datetime 
import shutil
import zipfile
import base64
import itertools

from http import HTTPStatus
from typing import Callable
from datetime import datetime as dttime

from .serializers import UserSerializer
from .permission import IsOwnerOrReadOnly
    
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from polls.views import handle_uploaded_file, iterate_folder_2levels
from ku_djangoo.settings import BASE_DIR, ROOT_TEMP, ROOT_DATASET_DIR, ROOT_MODEL_DIR
from ku_djangoo.minio_utils import minio_service
from ku_djangoo.utils import get_unique_model_directory, get_unique_dataset_directory

EXAMPLE_PUBLIC_DATASET_DIRECTORY = "asset/user/dataset/1-20241107_192036-CS_dataset"
EXAMPLE_PRIVATE_DATASET_DIRECTORY = "asset/user/dataset/1-20241209_172716-CS_dataset"
DATASET_BASE_FOLDER_NAME_REGEX = "\/\d+-\d{8}_\d{6}-[^\/]+\/"

FILE_TYPES_DICT = {
    '.txt': 'text/plain',
    '.yaml': 'text/plain',
    '.yml': 'text/plain',
    '.csv': 'text/csv',
    '.js': 'text/javascript',
    '.xml': 'text/xml',
    '.html': 'text/html',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml',
    '.tiff': 'image/tiff',
    '.tif': 'image/tif',
    '.bmp': 'image/bmp',
    '.gif': 'image/gif',
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.ogg': 'audio/ogg',
    '.oga': 'audio/ogg',
    '.aac': 'audio/aac',
    '.flac': 'audio/flac',
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.ogv': 'video/ogg',
    '.avi': 'video/x-msvideo',
    '.mov': 'video/quicktime',
    '.zip': 'application/zip',
    '.json': 'application/json',
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
    ".rar": "application/vnd.rar",
    ".7z": "application/x-7z-compressed",
    ".bz2": "application/x-bzip2",
    ".xz": "application/x-xz",
    ".tgz": "application/gzip",
    ".tbz2": "application/x-bzip2",
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".exe": "application/vnd.microsoft.portable-executable",
    ".apk": "application/vnd.android.package-archive",
    ".jar": "application/java-archive", 
    ".war": "application/x-war", 
    ".ear": "application/x-ear", 
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
}

LOGIN_EXPIRED_RESPONSE = JsonResponse(
    {"message": "Please re-login, your login has expired."},
    status=status.HTTP_401_UNAUTHORIZED
)

INVALID_LOGIN_RESPONSE = JsonResponse(
    {"message": "Invalid credentials"}, 
    status=status.HTTP_401_UNAUTHORIZED
)

ONLY_GET_REQUEST_RESPONSE = Response(
    {"message": "Only GET request is available."}, 
    status=status.HTTP_400_BAD_REQUEST
)

REQUIRED_ZIP_FILE_MISSING_RESPONSE = JsonResponse({
    'message': 'The required zipfile is not uploaded.'
})

ONLY_ZIP_FILE_TYPE_RESPONSE = JsonResponse({
    "error": "Unable to extract the zip file. Please ensure to give the .zip file type."}, 
    status=400
)
NO_ACCESS_PERMISSION_JSON_RESPONSE = JsonResponse({
    'success': False, 
    'message': 'No access permission.'
})
NOT_FOUND_INVALID_QUERY_OR_DELETED_RECORD_JSON_RESPONSE = JsonResponse({
    'success': False, 
    'message': 'Not found - Invalid query or deleted record.'
})
SUCCESS_JSON_RESPONSE = JsonResponse({
    'success': True
})
AUTHENTICATION_REQUIRED_JSON_RESPONSE = JsonResponse({
    "error": "Authentication required"}, 
    status=HTTPStatus.UNAUTHORIZED
)
PLEASE_LOGIN_JSON_RESPONSE = JsonResponse({
    'success': False, 
    'message': 'Please login.'
})
NO_PERMISSION_TO_TAKE_THE_ACTION_RESPONSE = JsonResponse({
    'success': False, 
    'message': 'No permission to take the action.'
})

SUCCESSFUL_ZIP_FILE_UPLOAD_RESPONSE = Response({
    'message': 'Successfully uploaded your zip file and saved them into our records.',
})

NO_ACCESS_PERMISSION_RESPONSE = Response({
    'success': False, 
    'message': 'No access permission.'
})
NOT_FOUND_INVALID_ID_OR_DELETED_RECORD_RESPONSE = Response({
    'success': False, 
    'message': 'Not found - Invalid ID or deleted record.'
})
NOT_FOUND_INVALID_QUERY_OR_DELETED_RECORD_RESPONSE = Response({
    'success': False, 
    'message': 'Not found - Invalid query or deleted record.'
})
DATASET_NOT_FOUND_INVALID_ID_OR_DELETED_RECORD_RESPONSE = Response({
    'success': False, 
    'message': 'Dataset not found - Invalid ID or deleted record.'
})

def get_model_directory(model: Model) -> str:
    return model.model_directory

def get_dataset_directory(dataset: Dataset) -> str:
    return dataset.dataset_directory

class ModelSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Model
        fields = ["id", "name", "updated", "is_public", "original_model", "model_type", "username", "model_directory", "description"]

class DatasetSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Dataset
        fields = ["id", "name", "updated", "created", "is_public", "original_dataset", "username", "dataset_directory", "description"]

class UserSerializer_(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "email", "last_login", "date_joined", "url", "groups"]

class ModelList(generics.ListCreateAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DatasetList(generics.ListCreateAPIView):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ModelDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                      IsOwnerOrReadOnly]
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

class DatasetDetail_(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                      IsOwnerOrReadOnly]
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

class UserDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                      IsOwnerOrReadOnly]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProtectedDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is protected data"})

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return LOGIN_EXPIRED_RESPONSE
        
        try:
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)
            response = Response({
                "success": True
                , 'access_token': new_access_token
            })
            response.set_cookie("access_token", new_access_token, httponly=True)
            return response
        except InvalidToken:
            return Response({'detail': "Invalid Token - Cannot refresh access token."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': "Failed to refresh access token."}, 
                            status=status.HTTP_400_BAD_REQUEST)

def identify_user_from_jwt_access_token_from_cookie(request):
    auth = JWTAuthentication()
    try:
        validated_token = auth.get_validated_token(request.COOKIES.get('access_token'))
        user = auth.get_user(validated_token)
        return user
    except InvalidToken:
        return None

def get_user_id_from_jwt_refresh_token(request):
    try:
        refresh_token = request.COOKIES.get('refresh_token')
        token = RefreshToken(refresh_token)
        user_id = token['user_id']
        return user_id
    except:
        return None

def get_user_from_jwt_refresh_token_from_cookie(request):
    """
    Database querying, less efficient than function identify_user_from_jwt_access_token.
    Only recommended as second option.
    """
    user_id = get_user_id_from_jwt_refresh_token(request)
    
    if user_id == None:
        return None
    
    try:
        user = User.objects.get(id=user_id) 
    except:
        return None

    return user

def identify_user_from_jwt_token_from_cookie(request):
    user = identify_user_from_jwt_access_token_from_cookie(request)
        
    if user == None:
        user = get_user_from_jwt_refresh_token_from_cookie(request)
        
    return user

class TestUserInfoAndCookie(APIView):
    authentication_classes = [] 
    permission_classes = []

    def post(self, request, *args, **kwargs):
        
        user = identify_user_from_jwt_token_from_cookie(request)

        if user == None:
            return LOGIN_EXPIRED_RESPONSE

        assert user.is_authenticated == True, "The user must have been authenticated."
        assert user.is_active == True, "User is inactive, they may have logged out."
        assert user.is_anonymous == False, "The authenticated user must not be anonymous."
        
        response = JsonResponse({
            "detail": "Test cookie, token and user identification finished."
        })

        return response

class CustomLoginTokenAccessView(APIView):
    
    authentication_classes = [] 
    permission_classes = []

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if not user:
            return INVALID_LOGIN_RESPONSE
        
        login(request, user)
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = JsonResponse({
            "success": True,
            "is_logged_in": True,
            "username": user.username,
        })
        response.set_cookie(
            "access_token", 
            access_token, 
            httponly=True, 
            secure=False, 
            expires=dttime.now(datetime.UTC) + datetime.timedelta(hours=1),
        )
        response.set_cookie(
            "refresh_token", 
            refresh_token, 
            httponly=True, 
            secure=False, 
            expires=dttime.now(datetime.UTC) + datetime.timedelta(hours=7),
        )

        return response

class CustomLogoutTokenView(APIView):

    authentication_classes = [JWTAuthentication] 
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({"detail": "Refresh token not found in cookies.", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response({"detail": "Successfully logged out.", "is_logged_in": False}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')
            return response
        except InvalidToken:
            return Response({"detail": "Invalid refresh token.", "success": False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"detail": "An Error occured during logout.", "success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomCheckLoginStateTokenView(APIView):
    authentication_classes = [JWTAuthentication] 
    permission_classes = []
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"is_logged_in": False}, status=status.HTTP_200_OK)
        try:
            token = RefreshToken(refresh_token)
            return Response({"is_logged_in": True}, status=status.HTTP_200_OK)
        except InvalidToken:
            response = Response({"is_logged_in": False}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')
            return response
        except TokenError: 
            response = Response({"is_logged_in": False}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')
            return response
        except Exception as e:
            print(f"Unexpected error during login check: {e}")
            response = Response({"is_logged_in": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')
            return response
    
def empty_default_authentication_classes_and_permission_classes(view_func):
    @authentication_classes([]) 
    @permission_classes([]) 
    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapped_view

@api_view(['GET'])
@authentication_classes([]) 
@permission_classes([]) 
def model_list_user(request, format=None):
    if request.method == 'GET':
        user = identify_user_from_jwt_token_from_cookie(request)

        if user == None:
            return Response(get_model_list().data)

        models = Model.objects.filter(
            (Q(is_public=False
               , user=user) 
            | Q(is_public=True)))[:10]
        serializer = ModelSerializer(models, many=True)
        return Response(serializer.data)
    
    return ONLY_GET_REQUEST_RESPONSE

@api_view(['GET'])
@authentication_classes([]) 
@permission_classes([]) 
def dataset_list_user(request, format=None):
    if request.method == 'GET':
        user = identify_user_from_jwt_token_from_cookie(request)

        if user == None:
            return Response(get_dataset_list().data)
            
        datasets = Dataset.objects.filter(
            (Q(is_public=False
               , user=user) 
            | Q(is_public=True)))[:10]
        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)
    
    return ONLY_GET_REQUEST_RESPONSE

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def user_profile(request, format=None):
    if request.method == 'GET':
        user = identify_user_from_jwt_token_from_cookie(request)
        
        if user == None: 
            return LOGIN_EXPIRED_RESPONSE
        
        serializer = UserSerializer_(user, many=False, context={'request': request})
        return Response(serializer.data)
        
    return ONLY_GET_REQUEST_RESPONSE

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def user_login_check(request, format=None):    
    if request.method == 'GET':
        user = identify_user_from_jwt_token_from_cookie(request)

        if user == None:
            return LOGIN_EXPIRED_RESPONSE

        if user != None:
            return Response({
                "detail": "You are logged in.", 
                "username": user.username, 
                "user_is_authenticated": True,
            })

    return ONLY_GET_REQUEST_RESPONSE

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def user_private_models(request, format=None):
    
    if request.method == 'GET':        
        user = identify_user_from_jwt_token_from_cookie(request)
        
        if user == None:
            return LOGIN_EXPIRED_RESPONSE

        models = Model.objects.filter(is_public=False, user=user)[:10]
        serializer = ModelSerializer(models, many=True)
        return Response(serializer.data)
    
    return ONLY_GET_REQUEST_RESPONSE        

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def user_private_datasets(request, format=None):
    
    if request.method == 'GET':        
        user = identify_user_from_jwt_token_from_cookie(request)
        
        if user == None:
            return LOGIN_EXPIRED_RESPONSE

        datasets = Dataset.objects.filter(is_public=False, user=user)[:10]
        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)
    
    return ONLY_GET_REQUEST_RESPONSE

def get_json(request):
    return json.loads(request.body)

def now_Ymd_HMS(format='%Y%m%d_%H%M%S') -> str:
    return timezone.now().strftime(format)

def save_zip_bytes_file(bytes, filename='a_zip_file.zip', root_dir=ROOT_TEMP):
    with open(os.path.join(root_dir, filename), "wb") as binary_file:
        binary_file.write(bytes)
    return

def save_zip_file(zipfile, timestamp: str, extension: str ='.zip', root_dir: str = ROOT_TEMP, name=''):
    filename = f'{zipfile}' or '_'
    try:
        filename = zipfile.name or '_'        
    except Exception as e:
        print('Failed to get name from zipfile/TemporaryUploadedFile', e)

    for extension_ in ['.zip', '.7z', '.tar.xz']:
        if filename.endswith(extension_):
            extension = ''
    
    # TODO - update old directory format to new.
    save_filename = f"{name}{extension}"
    zipfile_dir = os.path.join(root_dir, save_filename)

    FileSystemStorage(location=root_dir).save(save_filename, zipfile)     
    return zipfile_dir

@api_view(['POST'])
def login_api(request):
    body = request.body
    data = json.loads(body)

    username = data["username"]
    password = data["password"]
    user = authenticate(request, username=username, password=password)
    
    response_data = {
        "username": username, 
    }

    request.session._get_or_create_session_key()
    
    if user is not None or request.user.is_authenticated:
        login(request, user)
        response_data['is_authenticated'] = True
        token, created = Token.objects.get_or_create(user=user)
        response_data["token"] = token
        return JsonResponse(response_data)
    
    return JsonResponse(response_data)

@csrf_exempt
def get_models_api(request):
    models = (
        Model.objects
        .filter(is_public=True)
        .select_related("user")
        .order_by("-created")[:5]
    )

    models_serializer = ModelSerializer(models, many=True)

    response_data = {
        "models": models_serializer.data
    }
    return JsonResponse(response_data)

@csrf_exempt
def get_datasets_api(request):
    datasets = (
        Dataset.objects
        .filter(is_public=True)
        .select_related("user")
        .order_by("-created")[:5]
    )
    
    datasets_json = DatasetSerializer(datasets, many=True)

    response_data = {
        "datasets": datasets_json.data
    }
    return JsonResponse(response_data)

@api_view(['GET', 'POST'])
@authentication_classes([]) 
@permission_classes([]) 
def models(request, format=None):
    """
    List all models, or create a new model.
    """
    if request.method == 'GET':
        models = Model.objects.all()[:10]
        serializer = ModelSerializer(models, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([]) 
@permission_classes([]) 
def dataset_list(request):
    if request.method == 'GET':
        datasets = Dataset.objects.all()[:10]
        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)
    return ONLY_GET_REQUEST_RESPONSE

def get_model_list():
    models = Model.objects.filter(is_public=True)[:10]
    serializer = ModelSerializer(models, many=True)
    return serializer

def get_dataset_list():
    datasets = Dataset.objects.filter(is_public=True)[:10]
    serializer = DatasetSerializer(datasets, many=True)
    return serializer

@csrf_exempt
def test_list_random_values(request, format=None):    
    data = {
        'one': str(random.randint(1, 100)),
        'two': str(random.randint(1, 100)),
        'username': request.user.username
    }

    return JsonResponse(data)

@api_view(['GET'])
def test_get_with_token_authorisation(request, format=None):    
    data = {
        'one': str(random.randint(1, 100)),
        'two': str(random.randint(1, 100)),
        'username': request.user.username
    }

    return JsonResponse(data)

def get_zipfile(request, name):
    zipfile_list = request.FILES.getlist(name)
    zipfile_ = request.FILES.get(name)

    if zipfile_ != None and len(zipfile_) != 0:
        return zipfile_

    if type(zipfile_list == list) and len(zipfile_list) != 0:
        zipfile = zipfile_list[0] 
        if zipfile != None:
            return zipfile

    return None

def check_is_zipfile(zipfile, ):
    if zipfile != None:
        for extension in ('.zip','.7zip', '.rar','.7z'):
            if zipfile.name.endswith(extension):
                return True
    return False

@DeprecationWarning
def get_unique_directory_deprecated(filename: str, user_id, root_dir: str):
    """
    @deprecated. use get_unique_directory instead.
    """
    timestamp = now_Ymd_HMS()
    filename_, file_extension = path_split(filename)
    # TODO - update old directory format to new.
    unique_filename = f"{user_id}-{timestamp}-{filename_}"
    save_directory = os.path.join(root_dir, unique_filename)
    return save_directory, timestamp, unique_filename, filename_, file_extension

@DeprecationWarning
def get_unique_model_directory_deprecated(filename: str, user_id, root_dir: str = ROOT_MODEL_DIR):
    return get_unique_directory_deprecated(filename, user_id, root_dir) 

@DeprecationWarning
def get_unique_dataset_directory_deprecated(filename: str, user_id, root_dir: str = ROOT_DATASET_DIR):
    return get_unique_directory_deprecated(filename, user_id, root_dir) 

def get_dataset_form_data(request, namespace = '', zipfile_namespace = 'dataset_') -> tuple[str, str, str, any]:
    name = request.POST.get(f'{namespace}name')
    is_public = request.POST.get(f'{namespace}is_public')
    description = request.POST.get(f'{namespace}description')
    dataset_zipfile = get_zipfile(request, f'{zipfile_namespace}zipfile')
    return name, is_public, description, dataset_zipfile

def get_model_form_data(request, namespace = '', type_namespace = 'model_', zipfile_namespace = 'model_') -> tuple[str, str, str, str, any]:
    name, is_public, description, model_zipfile = (
        get_dataset_form_data(request, namespace, zipfile_namespace)
    )
    model_type = request.POST.get(f'{type_namespace}type')
    return name, model_type, is_public, description, model_zipfile

@api_view(['POST'])
@authentication_classes([]) 
@permission_classes([]) 
def model_form_post(request, format=None):
    user = identify_user_from_jwt_token_from_cookie(request)
    if user == None:
        return LOGIN_EXPIRED_RESPONSE
    
    user, response = identify_user_from_jwt_token_from_cookie_with_response(request)
    if response: return response

    model_name, model_type, is_public, description, model_zipfile = get_model_form_data(request)
    
    if model_zipfile == None or len(model_zipfile) == 0:
        return REQUIRED_ZIP_FILE_MISSING_RESPONSE

    save_directory, _, _, _, _ = get_unique_model_directory(str(user.id), model_name)
    
    try:
        handle_extract_zip_file(model_zipfile, save_directory)
        save_model_folder_info_to_database(model_name, user, model_type, save_directory, is_public, description=description)
    except ValueError:
        return ONLY_ZIP_FILE_TYPE_RESPONSE

    return SUCCESSFUL_ZIP_FILE_UPLOAD_RESPONSE

def path_split(path: str) -> tuple[str, str]:
    """
    split filename and extension
    """
    return os.path.splitext(path)

def get_file_extension(file_path):
    """Gets the file extension"""
    _, ext = os.path.splitext(file_path)
    if ext:  
        return ext.lower() 
    return ""

@api_view(['POST'])
@authentication_classes([]) 
@permission_classes([]) 
def dataset_form_post(request, format=None):
    user = identify_user_from_jwt_token_from_cookie(request)
    if user == None:
        return LOGIN_EXPIRED_RESPONSE

    name, is_public, description, dataset_zipfile = get_dataset_form_data(request)
    
    if dataset_zipfile == None or len(dataset_zipfile) == 0:
        return REQUIRED_ZIP_FILE_MISSING_RESPONSE
    
    save_directory, _, _, _, _ = get_unique_dataset_directory(str(user.id), name)
    
    try:
        handle_extract_zip_file(dataset_zipfile, save_directory)
        save_dataset_to_database(name, user, save_directory, is_public, description=description)        
    except ValueError:
        return ONLY_ZIP_FILE_TYPE_RESPONSE

    return SUCCESSFUL_ZIP_FILE_UPLOAD_RESPONSE

def user_and_public_objects_pages(request, object=Model, objectSerializer=ModelSerializer, namespace='model_'):
    user = identify_user_from_jwt_token_from_cookie(request)
    objects = []
    
    if user == None:
        objects = object.objects.filter(is_public=True)

    if user != None:
        objects = object.objects.filter(is_public_or_is_user_private(user))

    serializer = objectSerializer(objects, many=True)
    serializer_data = serializer.data

    per_page = request.GET.get("per_page", 2)
    per_page = request.GET.get(f"{namespace}per_page", per_page)
    paginator = Paginator(serializer_data, per_page)
    page_num = request.GET.get(f"{namespace}page")
    page = paginator.get_page(page_num)

    return Response({
        'user': str(user),
        'page_number': page.number,
        'list': page.object_list,
        'total_list_count': page.paginator.count,
        'paginator_num_pages': page.paginator.num_pages,
        'page_has_next': page.has_next(),
        'page_has_previous': page.has_previous(),
    })

def get_page_range(current_page, total_pages, neighbors=2):
    if total_pages <= 1:
        return []

    pages = []
    pages.append(1)

    if current_page > neighbors + 2:
        pages.append("...")

    start = max(2, current_page - neighbors)
    end = min(total_pages - 1, current_page + neighbors)

    pages.extend(range(start, end + 1))

    if current_page < total_pages - neighbors - 1:
        pages.append("...")

    pages.append(total_pages)

    return pages

@api_view(['GET'])
@authentication_classes([]) 
@permission_classes([]) 
def test_page_range(request):
    queryset = Dataset.objects.filter(is_public=True)    
    serializer = DatasetSerializer(queryset, many=True)
    serializer_data = serializer.data
    
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 1)
    paginator = Paginator(serializer_data, per_page)
    current_page = paginator.get_page(page)

    page_range = get_page_range(current_page.number, paginator.num_pages)
    
    return JsonResponse({
        "list": current_page.object_list,
        "current_page": current_page.number,
        "page_range": page_range,
        'total_list_count': paginator.count,
        'num_pages': paginator.num_pages,
        'page_has_next': current_page.has_next(),
        'page_has_previous': current_page.has_previous(),
    })

def datasets_page_range_function(request, Object=Dataset, Serializer=DatasetSerializer):
    user = identify_user_from_jwt_token_from_cookie(request)
    queryset = []

    if user == None:
        queryset = Object.objects.filter(is_public=True)
    
    if user != None:        
        queryset = Object.objects.filter(is_public_or_is_user_private(user))
        
    serializer = Serializer(queryset, many=True)
    serializer_data = serializer.data
    
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 1)
    paginator = Paginator(serializer_data, per_page)
    current_page = paginator.get_page(page)

    page_range = get_page_range(current_page.number, paginator.num_pages)
    
    return JsonResponse({
        "list": current_page.object_list,
        "current_page": current_page.number,
        'page_has_next': current_page.has_next(),
        'page_has_previous': current_page.has_previous(),
        "page_range": page_range,
        'total_list_count': paginator.count,
        'num_pages': paginator.num_pages,
    })

@api_view(['GET'])
@authentication_classes([]) 
@permission_classes([]) 
def datasets_page_range(request):
    return datasets_page_range_function(request, Object=Dataset, Serializer=DatasetSerializer)

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def models_page_range(request):
    return datasets_page_range_function(request, Object=Model, Serializer=ModelSerializer)

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def user_and_public_models_pages(request):
    return user_and_public_objects_pages(request, object=Model, objectSerializer=ModelSerializer, namespace='model_')

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def user_and_public_datasets_pages(request):
    return user_and_public_objects_pages(request, object=Dataset, objectSerializer=DatasetSerializer, namespace='dataset_')

@api_view(['GET', 'POST'])
@empty_default_authentication_classes_and_permission_classes
def search_model_by_name(request):
    user = identify_user_from_jwt_token_from_cookie(request)
   
    models = []
    q = request.GET.get("query")
    LIMIT = 5

    if request.method == "POST":
        q = request.POST.get("query", q)
    
    if q:
        models = Model.objects.filter(
            Q(name__icontains=q)
            & is_public_or_is_user_private(user)
        )[:LIMIT]

    if not models:
        models = Model.objects.all()[:LIMIT]

    objectSerializer = ModelSerializer
    objects = models

    serializer = objectSerializer(objects, many=True)
    serializer_data = serializer.data
    
    data = {
        "search_model_query_value": q, 
        "list": serializer_data
    }
    return Response(data)

HTTP_METHOD_NAMES = [
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
    "trace",
]

class DatasetDetail(APIView):
    authentication_classes = [] 
    permission_classes = []

    def get(self, request, id):
        user = identify_user_from_jwt_token_from_cookie(request)
        try:
            dataset = Dataset.objects.get(id=id)            
            if dataset and (not dataset.is_public) and dataset.user != user:
                print('no access permission response')
                return NO_ACCESS_PERMISSION_RESPONSE
        except Dataset.DoesNotExist:
            return NOT_FOUND_INVALID_ID_OR_DELETED_RECORD_RESPONSE

        serializer = DatasetSerializer(dataset)
        serializer_data = serializer.data
        readme_markdown = search_and_get_readme_markdown_by_directory(dataset.dataset_directory)
        serializer_data['markdown'] =  readme_markdown
        return Response(serializer_data)
    
    def delete(self, request, id):
        user = identify_user_from_jwt_token_from_cookie(request)
        
        if user == None:
            return Response({'success': False, 'message': 'Please login to delete your dataset.'})

        try:
            dataset = Dataset.objects.get(id=id, user=user)            
            success = remove_directory(dataset.dataset_directory)
            if success:
                dataset.delete()
                return Response({'success': True, 'message': 'Delete Success.'})
            if not success:
                return Response({'success': False, 'message': 'Dataset directory not found.'})
        except Dataset.DoesNotExist:
            return Response({'success': False, 'message': 'Dataset not found.'})

class ModelDetail(APIView):
    authentication_classes = [] 
    permission_classes = []

    def get(self, request, id):
        user = identify_user_from_jwt_token_from_cookie(request)

        try:
            model = Model.objects.get(id=id)
            if model and not model.is_public and model.user != user:
                return NO_ACCESS_PERMISSION_RESPONSE
        except Model.DoesNotExist:
            return NOT_FOUND_INVALID_ID_OR_DELETED_RECORD_RESPONSE
        
        serializer = ModelSerializer(model)
        serializer_data = serializer.data
        readme_markdown = search_and_get_readme_markdown_by_directory(model.model_directory)
        serializer_data['markdown'] =  readme_markdown
        return Response(serializer_data)
    
    def delete(self, request, id):
        user = identify_user_from_jwt_token_from_cookie(request)
        
        if user == None:
            return Response({'success': False, 'message': 'Please login to delete your model.'})

        try:
            model = Model.objects.get(id=id, user=user)            
            success = remove_directory(model.model_directory)
            if success:
                model.delete()
                return Response({'success': True, 'message': 'Delete Success.'})
            if not success:
                return Response({'success': False, 'message': 'Model directory not found.'})
        except Model.DoesNotExist:
            return Response({'success': False, 'message': 'Model not found.'})

def remove_directory(dir):
    if os.path.exists(dir) and os.path.isdir(dir):
        shutil.rmtree(dir)
        return True
    return False

def is_public_or_is_user_private(user):
    return (
        Q(is_public=True)
        | Q(is_public=False, user=user)
    )

BASE_TMP_DIR = os.path.join(BASE_DIR, 'tmp')

def make_zip_path(path: str) -> str:
    zip_filename = f'{path_normpath_basename(path)}.zip'
    zip_path = os.path.join(BASE_TMP_DIR, zip_filename)
    return zip_filename, zip_path

def download_zip(folder_path: str):    
    _, zip_path = make_zip_path(folder_path)

    if not any(os.scandir(folder_path)):
        return "No files scanned/found to zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))

    return zip_path    

def is_not_public_and_not_owner(obj, user):
    return not obj.is_public and obj.user != user

def obj_and_is_not_public_and_not_owner(obj, user):
    return obj and is_not_public_and_not_owner(obj, user)

def check_obj_exist_and_user_has_access_permission(obj, user):
    if not obj:
        return NOT_FOUND_INVALID_QUERY_OR_DELETED_RECORD_JSON_RESPONSE
    
    if obj_and_is_not_public_and_not_owner(obj, user):       
        return NO_ACCESS_PERMISSION_JSON_RESPONSE
    
    return None

def remove_temp_path(path: str):
    os.remove(path)

def download_obj_zip(request, id, Obj, get_obj_directory: Callable):
    user = identify_user_from_jwt_token_from_cookie(request)
    try:
        obj = Obj.objects.get(id=id)
    except Obj.DoesNotExist:
        return NOT_FOUND_INVALID_ID_OR_DELETED_RECORD_RESPONSE
    
    if not obj.is_public and obj.user != user:
        return NO_ACCESS_PERMISSION_RESPONSE

    folder_path = get_obj_directory(obj)
    
    zip_path = download_zip(folder_path)
    
    if zip_path == "No files scanned/found to zip":
        return HttpResponse(zip_path, status=400)
    
    with open(zip_path, 'rb') as zip_file:        
        zip_filename = f'{obj.name}.zip'
        response = HttpResponse(zip_file.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        remove_temp_path(zip_path)
        return response 



@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def download_dataset_zip(request, id):
    return download_obj_zip(request, id, Dataset, get_dataset_directory)

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def download_model_zip(request, id):
    return download_obj_zip(request, id, Model, get_model_directory)

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def test_download_dataset_zip(request):    
    folder_path = "static/dataset/CS_dataset"
    
    zip_filename, _ = make_zip_path(folder_path)

    zip_path = download_zip(folder_path)

    if zip_path == "No files scanned/found to zip":
        return HttpResponse(zip_path, status=400)
    
    with open(zip_path, 'rb') as zip_file:        
        response = HttpResponse(zip_file.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        return response 
    
    return 

def path_basename(path: str) -> str:
    """
    get file name. 

    in:
    /folderA/folderB/folderC/folderD/
    
    out:
    folderD
    """
    return os.path.basename(path)

def path_normpath(path: str) -> str:
    """
    to strip off any trailing slashes
    """
    return os.path.normpath(path)

def path_normpath_basename(path: str) -> str:
    return path_basename(path_normpath(path))

def download_zip_stream(request, id):
    """
    Streaming for large size data
    """
    user = identify_user_from_jwt_token_from_cookie(request)
    
    try:
        dataset = Dataset.objects.get(id=id)
    except Dataset.DoesNotExist:
        return DATASET_NOT_FOUND_INVALID_ID_OR_DELETED_RECORD_RESPONSE
    
    if not dataset.is_public and dataset.user != user:
        return NO_ACCESS_PERMISSION_RESPONSE

    zip_path = download_zip(dataset.dataset_directory)
    response = FileResponse(open(zip_path, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="files.zip"'
    return response

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def test_api(request):
    return Response({
        'message': 'this is test API',
    })

@api_view(['GET', 'PUT', 'DELETE'])
def model_detail(request, pk, format=None):
    """
    Retrieve, update or delete a model.
    """
    try:
        model = Model.objects.get(pk=pk)
    except Model.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ModelSerializer(model)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ModelSerializer(model, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def text_markdown_fenced_code_to_markdown(readme_text):
    readme_markdown = MARKDOWN_FENCED_CODE.convert(readme_text)
    return readme_markdown

def passfunc(s):
    return s

def preformat(txt):
    return f'<pre>{txt}</pre>'

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def get_dataset_image_api(request, user_id, dataset_name, image_path):
    return get_dataset_image(request, user_id, dataset_name, image_path)

def get_dataset_image(request, user_id, dataset_name, image_path, Object=Dataset, lookup_key='dataset_directory', get_unique_directory=get_unique_dataset_directory):
    dataset_directory = get_unique_directory(str(user_id), dataset_name)    
    file_path_ = f"{dataset_directory}/{image_path}"
    file_path = file_path_.rstrip('/')
    user = identify_user_from_jwt_token_from_cookie(request)
    content_type = ''
    file_read_type = 'rb'
    formatfunction = passfunc
    
    content_type = FILE_TYPES_DICT.get(get_file_extension(file_path))

    if (content_type == 'text/html'
        or
        content_type == 'text/plain'
    ):
        formatfunction = preformat
        file_read_type = 'r'    

    try:
        dataset = Object.objects.get(**{lookup_key: dataset_directory})
    except Exception as e:
        print(f'Dataset get query error: {e}')
        
    data = None

    if not dataset:
        print(' dataset not found')
        return HttpResponse(None, content_type=content_type)
    
    if dataset and not dataset.is_public and dataset.user != user:
        print(f' dataset: no access permission {dataset.is_public} {dataset.user} {user}')
        return HttpResponse(None, content_type=content_type)
    
    if os.path.exists(file_path_) and os.path.isdir(file_path_):        
        return get_dataset_file_tree(request, user_id, dataset_name, image_path)

    if ((dataset and dataset.is_public) 
        or 
        (dataset and not dataset.is_public and dataset.user == user)
        ):
        with open(file_path, file_read_type) as file:
            data = file.read()
            if "readme" in file_path.lower() or file_path.endswith(".md"):
                data = text_markdown_fenced_code_to_markdown(data)            
            data = formatfunction(data)

    return HttpResponse(data, content_type=content_type)

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def get_model_image(request, user_id, model_name, image_path):
    return get_dataset_image(request, user_id, model_name, image_path, Object=Model, lookup_key='model_directory', get_unique_directory=get_unique_model_directory)

def get_dataset_file_tree(request, user_id, dataset_name, path, Object=Dataset, root_dir=ROOT_DATASET_DIR, lookup_key='dataset_directory'):
    print(' get_dataset_file_tree ')
    dataset_base_directory = get_unique_dataset_directory(str(user_id), dataset_name, root_dir=root_dir)
    dataset_directory = os.path.join(dataset_base_directory, path)
    user = identify_user_from_jwt_token_from_cookie(request)
    if not os.path.exists(dataset_directory) or not os.path.isdir(dataset_directory):
        return JsonResponse({"error": "Invalid directory path"}, status=400)
    
    dataset = Object.objects.get(**{lookup_key: dataset_base_directory})

    if not dataset:
        return NOT_FOUND_INVALID_QUERY_OR_DELETED_RECORD_JSON_RESPONSE
    
    if dataset and not dataset.is_public and dataset.user != user:
        return NO_ACCESS_PERMISSION_JSON_RESPONSE

    try:
        files_and_dirs = os.listdir(dataset_directory)
        tree = []
        
        for item in files_and_dirs:
            full_path = os.path.join(dataset_directory, item)
            tree.append({
                "name": item,
                "is_dir": os.path.isdir(full_path),
                "size": os.path.getsize(full_path) if os.path.isfile(full_path) else None,
            })
        
        return JsonResponse({"path": dataset_directory, "tree": tree}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def find_file_path_for_two_tree_levels(directory, name_end):
    for path in iterate_folder_2levels(directory):
        if (path.name.endswith(name_end) 
            and path.is_file()
        ):
            return path
    return

def get_csv_data(request):
    csv_path = request.path.replace('/api/dataset/', '')
    csv_path = f"{ROOT_DATASET_DIR}{csv_path}"

    if not csv_path.endswith('.csv'):
        return HttpResponse("Path must end with '.csv'.", status=404)
    
    user = identify_user_from_jwt_token_from_cookie(request)    
    
    dataset_base_directory = csv_path.replace('/.csv', '')
    
    csv_path = find_file_path_for_two_tree_levels(dataset_base_directory, '.csv')

    dataset = Dataset.objects.get(dataset_directory = dataset_base_directory)
    
    response = check_obj_exist_and_user_has_access_permission(dataset, user)
    if response: return response
    
    num_of_rows_to_read = 61
    csv_data = []

    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile: 
            reader = csv.reader(csvfile)
            
            limited_rows = list(itertools.islice(reader, num_of_rows_to_read))
            csv_data = '\n'.join([','.join(row) for row in limited_rows])

        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data.csv"' 
        return response
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)

@api_view(['POST'])
@empty_default_authentication_classes_and_permission_classes
def fork_model_api(request):

    return SUCCESS_JSON_RESPONSE

@api_view(['POST'])
@empty_default_authentication_classes_and_permission_classes
def fork_dataset_api(request):
    user = identify_user_from_jwt_token_from_cookie(request)    
    print(user)
    if not user:
        return AUTHENTICATION_REQUIRED_JSON_RESPONSE
    
    dataset_id = request.POST.get('dataset_id')
    dataset_name = request.POST.get('name')
    ispublic = request.POST.get('is_public')
    description = request.POST.get('description')

    fork_dataset(dataset_id, user, dataset_name, ispublic, description=description)
    return SUCCESS_JSON_RESPONSE

def store_temporary_file(file, filename='afile', base_tmp_dir="tmp/", file_extension=''):
    handle_uploaded_file(file, filename=filename, dir=base_tmp_dir, file_extension=file_extension)
    return os.path.join(base_tmp_dir, f"{filename}{file_extension}")

@api_view(['POST'])
@empty_default_authentication_classes_and_permission_classes
def save_dataset_file_to_minio_api(request):
    return save_dataset_file_to_minio(request)

def save_dataset_file_to_minio(request, pathbase='dataset/'):
    user = identify_user_from_jwt_token_from_cookie(request)
    if not user:
        return AUTHENTICATION_REQUIRED_JSON_RESPONSE
    
    namespace = ''
    dataset_name = 'data'
    file = request.FILES.get(f'{namespace}{dataset_name}')
    filename = 'file'
    if file:
        filename = file.name
    file_basename = os.path.basename(filename)
    sanitized_filename = file_basename.replace(" ", "_")
    temp_dir = store_temporary_file(file, filename=sanitized_filename)
    source_file = temp_dir
    object_name = f'{pathbase}{sanitized_filename}'
    minio_service.save_file_as_object(object_name, source_file)
    return SUCCESS_JSON_RESPONSE

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def read_dataset_from_minio(request, id):
    dataset, response = Dataset_get(id)
    if response: return response
    user, response = identify_user_from_cookie_jwt_token_and_check_obj_user_access_permission(request, dataset)
    if response: return response
    
    dataset_dir = dataset.dataset_directory.replace(ROOT_DATASET_DIR, '')
    dataset_dir = dataset_dir.rstrip('/')
    
    if not dataset_dir.startswith('dataset/'):
        dataset_dir = f'dataset/{dataset_dir}'

    file_extension = get_file_extension(dataset_dir)
    content_type = FILE_TYPES_DICT.get(file_extension)
    if not content_type:
        file_content, status_code = minio_service.get_zipped_file(dataset_dir)
        content_type = 'application/zip'
        file_extension = '.zip'
    else:
        file_content = minio_service.read_file_from_minio(dataset_dir)
    
    response = HttpResponse(file_content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{dataset_dir}{file_extension}"'
    return response

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def test_get_zip_file_from_minio(request):
    object_name = 'CS_dataset.zip'
    file_content = minio_service.read_file_from_minio(object_name)
    response = HttpResponse(file_content, content_type='application/zip') #  application/zip or application/octet-stream
    response['Content-Disposition'] = f'attachment; filename="my_zip.zip"'
    return response

def Dataset_get(id):
    try:
        return Dataset.objects.get(id=id), None
    except Exception as e:
        print(f"Error getting a dataset: {e}")
        return None, DATASET_NOT_FOUND_INVALID_ID_OR_DELETED_RECORD_RESPONSE

def Dataset_filter(condition):
    try:
        return Dataset.objects.filter(condition), None
    except Exception as e:
        print(f"Error filtering dataset: {e}")
        return None, DATASET_NOT_FOUND_INVALID_ID_OR_DELETED_RECORD_RESPONSE

def identify_user_from_jwt_token_from_cookie_with_response(request):
    user = identify_user_from_jwt_token_from_cookie(request)
    if user == None:
        return None, AUTHENTICATION_REQUIRED_JSON_RESPONSE
    return user, None

def identify_user_from_cookie_jwt_token_and_check_obj_user_access_permission(request, dataset):
    user = identify_user_from_jwt_token_from_cookie(request)
    if user == None:
        return None, AUTHENTICATION_REQUIRED_JSON_RESPONSE
    response = check_obj_exist_and_user_has_access_permission(dataset, user)
    return user, response

@api_view(['DELETE'])
@empty_default_authentication_classes_and_permission_classes
def delete_dataset_file_from_minio(request, id):
    dataset, error = Dataset_get(id)
    if error: return error

    user, response = identify_user_from_cookie_jwt_token_and_check_obj_user_access_permission(request, dataset)
    if response: return response

    object_name = 'dataset/'
    success = minio_service.remove_object(object_name)
    if success:
        return JsonResponse({}, status=HTTPStatus.NO_CONTENT)
    else:
        return JsonResponse({'error': 'Failed to delete object'}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def list_minio_bucket_object(request):
    minio_service.print_list_object()
    object_name = 'CS_dataset.zip'
    success = minio_service.check_object_deleted(object_name)
    print(success)
    file_content = minio_service.read_file_from_minio(object_name)
    response = HttpResponse(file_content, content_type='application/zip') 
    response['Content-Disposition'] = f'attachment; filename="my_zip.zip"'
    return response

@api_view(['PUT'])
@empty_default_authentication_classes_and_permission_classes
def update_dataset_file_in_minio(request, id, pathbase='dataset/'):
    dataset, error = Dataset_get(id)
    if error: return error

    user, response = identify_user_from_cookie_jwt_token_and_check_obj_user_access_permission(request, dataset)
    if response: return response

    namespace = ''
    dataset_name = 'data'
    file = request.FILES.get(f'{namespace}{dataset_name}')
    filename = 'file'
    if file:
        filename = file.name
    file_basename = os.path.basename(filename)
    sanitized_filename = file_basename.replace(" ", "_")
    object_name = sanitized_filename
    temp_dir = store_temporary_file(file, filename = object_name)
    source_file = temp_dir
    minio_service.save_file_as_object(object_name, source_file)
    return SUCCESS_JSON_RESPONSE

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def read_file_from_minio_test(request):
    object_name = 'ppe_0000_jpg.rf.c102a9a7c8dec01565a8f95ff295974c.jpg'
    object_name = 'my-test-file.jpg'
    file_content = minio_service.read_file_from_minio(object_name)

    response = HttpResponse(file_content, content_type='image/jpg')
    response['Content-Disposition'] = f'attachment; filename="my_image.jpg"'
    return response

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def temp(request):
    delete_all_datasets_in_minio()
    return SUCCESS_JSON_RESPONSE

def upload_all_datasets_to_minio(local_dir=ROOT_MODEL_DIR, base_root='model'):
    """ Developer tool."""
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_file_path = os.path.join(root, file)
            object_name = os.path.relpath(local_file_path, local_dir)
            object_name = os.path.join(base_root, object_name)
            minio_service.save_file_as_object(object_name, local_file_path)
    return SUCCESS_JSON_RESPONSE

def delete_all_django_datasets_in_minio(local_dir=ROOT_DATASET_DIR, base_root='dataset'):
    # TODO remove all datasets and models in minio and upload_all_datasets_to_minio again.
    """ Developer tool."""
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_file_path = os.path.join(root, file)
            object_name = os.path.relpath(local_file_path, local_dir)
            minio_service.delete_all_object_versions(object_name)
    return SUCCESS_JSON_RESPONSE

def delete_all_datasets_in_minio(local_dir=ROOT_DATASET_DIR, base_root='dataset'):
    """ Developer tool."""
    local_dir='/data/bucket1/dataset'
    # minio_service.delete_all_object_versions(object_name)
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_file_path = os.path.join(root, file)
            # object_name = os.path.relpath(local_file_path, local_dir)
            print(local_file_path, local_dir)
            # minio_service.delete_all_object_versions(object_name)
    return SUCCESS_JSON_RESPONSE

def move_all_datasets_directory():
    """Developer tool."""
    destination_base_dir = 'asset/dataset/'
    
    os.makedirs(destination_base_dir, exist_ok=True)

    datasets = Dataset.objects.all()    
    for dataset in datasets:
        userid = dataset.user.id
        datasetname = dataset.name
        source_dir = dataset.dataset_directory
        destination_dir = f'{destination_base_dir}{userid}/{datasetname}'
        
        try:
            shutil.move(source_dir, destination_dir)
            dataset.dataset_directory = destination_dir
            dataset.save()
        except Exception as e:
            print(f"Error moving {source_dir}: {e}")

def move_all_models_directory():
    """Developer tool."""
    destination_base_dir = 'asset/model/'
    
    os.makedirs(destination_base_dir, exist_ok=True)

    models = Model.objects.all()    
    for model in models:
        userid = model.user.id
        modelname = model.name        
        source_dir = model.model_directory
        destination_dir = f'{destination_base_dir}{userid}/{modelname}'
        print(source_dir, ' -- ', destination_dir)
        
        try:
            shutil.move(source_dir, destination_dir)
            model.model_directory = destination_dir
            model.save()
        except Exception as e:
            print(f"Error moving {source_dir}: {e}")


@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def respond_dataset_file_tree(request, user_id, dataset_name, path=''):
    """
    API function to return a JSON object representing a tree of file paths limited to one level.
    """
    print(user_id, dataset_name, path)
    return get_dataset_file_tree(request, user_id, dataset_name, path)

@api_view(['GET'])
@empty_default_authentication_classes_and_permission_classes
def respond_model_file_tree(request, user_id, model_name, path=''):
    """
    API function to return a JSON object representing a tree of file paths limited to one level.
    """
    print(user_id, model_name, path)
    return get_dataset_file_tree(request, user_id, model_name, path, Object=Model, root_dir=ROOT_MODEL_DIR, lookup_key='model_directory')

@api_view(['GET'])
def get_request_username(request, pk, format=None):
    return JsonResponse({"username": request.user.username})

def test_path_split_ext():
    s = os.path.splitext("a/b/c.txt") 
    assert ("a/b/c", "txt") == s 
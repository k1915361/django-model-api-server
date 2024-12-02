from django.db.models import F
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Dataset, Model, ModelDataset
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .views import save_model_zip_file_and_to_model_database, ROOT_TEMP, save_and_extract_zip, handle_zip_file
import json
import uuid
import os 
import random
from django.utils import timezone

from rest_framework import generics
from .serializers import UserSerializer

from rest_framework import permissions
from .permission import IsOwnerOrReadOnly

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
    
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

LOGIN_EXPIRED_RESPONSE = JsonResponse(
    {"detail": "Please re-login, your login has expired."},
    status=status.HTTP_401_UNAUTHORIZED
)

INVALID_LOGIN_RESPONSE = JsonResponse(
    {"detail": "Invalid credentials"}, 
    status=status.HTTP_401_UNAUTHORIZED
)

class ModelSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Model
        fields = ["id", "name", "updated", "is_public", "original_model", "username"]

class DatasetSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Dataset
        fields = ["id", "name", "updated", "is_public", "original_dataset", "username"]

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

class DatasetDetail(generics.RetrieveUpdateAPIView):
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
            return Response({'detail': 'Refresh token missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)
            response = Response({
                "success": True
                , 'access_token': new_access_token
                , 'username': request.user.username
                , 'userid': request.user.id
                , 'user': str(request.user)
            })
            response.set_cookie("access_token", new_access_token, httponly=True)
            return response
        except InvalidToken:
            return Response({'detail': "Invalid Token - Cannot refresh access token."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': "Failed to refresh access token."}, 
                            status=status.HTTP_400_BAD_REQUEST)

def identify_user_from_jwt_access_token(request):
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

def get_user_from_jwt_refresh_token(request):
    """
    Database querying, less efficient than function identify_user_from_jwt_access_token.
    Only recommended as second option.
    """
    user_id = get_user_id_from_jwt_refresh_token(request)
    user = User.objects.get(id=user_id) 
    return user

class TestUserInfoAndCookie(APIView):
    authentication_classes = [] 
    permission_classes = []

    def post(self, request, *args, **kwargs):
        
        user = identify_user_from_jwt_access_token(request)
        
        if user == None:
            user = get_user_from_jwt_refresh_token(request)

        if user == None:
            return LOGIN_EXPIRED_RESPONSE

        assert user.is_authenticated == True, "The user must have been authenticated."
        assert user.is_active == True, "User is inactive, they may have logged out."
        assert user.is_anonymous == False, "The authenticated user must not be anonymous."
        
        response = JsonResponse({
            "detail": "Test cookie, token and user identification finished."
        })

        return response
import datetime 
from datetime import datetime as dttime

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

        print(' 1 ', request.user, request.user.is_authenticated)

        response = JsonResponse({
            "success": True,
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

def get_json(request):
    return json.loads(request.body)

def now_Ymd_HMS(format='%Y%m%d_%H%M%S') -> str:
    return timezone.now().strftime(format)

def save_zip_bytes_file(bytes, filename='a_zip_file.zip', root_dir=ROOT_TEMP):
    with open(os.path.join(root_dir, filename), "wb") as binary_file:
        binary_file.write(bytes)
    return

def save_zip_file(zipfile, timestamp: str, extension: str ='.zip', root_dir: str = ROOT_TEMP):
    filename = f'{zipfile}' or '_'
    try:
        filename = zipfile.name or '_'        
    except Exception as e:
        print('Failed to get name from zipfile/TemporaryUploadedFile', e)

    for extension_ in ['.zip', '.7z', '.tar.xz']:
        if filename.endswith(extension_):
            extension = ''
    
    save_filename = f"{timestamp}-{filename}{extension}"
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
    
    print(' --- 1: ', data)
    print(' --- login api(): ', username, password, type(data))

    response_data = {
        "username": username, 
    }

    print(' --- 2: ', response_data['token'].is_safe)    
    request.session._get_or_create_session_key()
    print(' --- 3: ', request.session.session_key)

    if user is not None or request.user.is_authenticated:
        login(request, user)
        response_data['is_authenticated'] = True
        token, created = Token.objects.get_or_create(user=user)
        response_data["token"] = token
        return JsonResponse(response_data)
    
    return JsonResponse(response_data)

@csrf_exempt
def upload_dataset_api(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'only POST is accepted'})
    
    body = request.body
    # data = json.loads(body)
    
    print(' - session key ', request.session._get_or_create_session_key()) # rae4vk5d4ajdrd8x0gx6w7gemr4b5424
    
    headers = request.headers
    # token = headers['token']

    # if token == request.session['token']:
        # print(' - request.session token matches the user token')

    FILESget_list = request.FILES.getlist
    POSTget = request.POST.get
    timestamp = now_Ymd_HMS()
    zip_bytes_file = FILESget_list('zip_bytes_file')
    zipfile = FILESget_list('zipfile')[0]
    name = POSTget("name")
    ispublic = POSTget("ispublic")    

    print(' zip_bytes_file')
    print(zip_bytes_file)
    print(' zipfile')
    print(zipfile)

    if len(zip_bytes_file) != 0:
        save_zip_file(zip_bytes_file, timestamp) 

    if len(zipfile) != 0:
        save_zip_file(zipfile, timestamp)

    # print(' --- login api(): ', name)

    response_data = {
        'upload_dataset_api function used': 'yes',
        "token": uuid.uuid4(),
    }

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
def model_list(request, format=None):
    """
    List all models, or create a new model.
    """
    if request.method == 'GET':
        models = Model.objects.all()
        serializer = ModelSerializer(models, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['POST'])
def test_model_form_post(request, format=None):
        
    name = request.POST.get('name')
    model_type = request.POST.get('model_type')
    is_public = request.POST.get('is_public')
    description = request.POST.get('description')
    model_zipfile = get_zipfile(request, 'model_zipfile')

    print('- ', model_zipfile)
    print('- ', name)
    print('- ', model_type)
    print('- ', is_public)
    print('- request.FILES', request.FILES)
    
    is_zipfile = check_is_zipfile(model_zipfile)

    if request.user.is_anonymous:
        return JsonResponse({'message': 'Please login to upload a file.'})

    if not is_zipfile:
        return JsonResponse({'message': 'Only .zip / .7zip / .rar / .7z files are allowed'}, status=400)

    timestamp = now_Ymd_HMS()

    if model_zipfile != None:
        model = save_model_zip_file_and_to_model_database(model_zipfile, name, request.user, model_type, is_public, timestamp, description=description, root_dir=ROOT_TEMP)
    elif model_zipfile == None:
        print('- zipfile is empty.')

    if model_zipfile != None:
        filename = f"{request.user.id}-{timestamp}-{model_zipfile.name}"
        extract_to = os.path.join(ROOT_TEMP, filename)

        try:
            handle_zip_file(model_zipfile, extract_to)
            message = "Zip file saved and extracted successfully"
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)

    data = {
        'response': 'success. response:',
        'name': name,
        'model_type': model_type,
        'is_public': is_public,
        'description': description,
    }

    return Response(data)

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
  
@api_view(['GET'])
def get_request_username(request, pk, format=None):
    return JsonResponse({"username": request.user.username})
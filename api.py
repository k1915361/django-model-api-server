from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import uuid
import os 
from .views import ROOT_TEMP
from django.utils import timezone

def get_json(request):
    return json.loads(request.body)

def now_Ymd_HMS(format='%Y%m%d_%H%M%S') -> str:
    return timezone.now().strftime(format)

def save_zip_bytes_file(bytes, filename='a_zip_file.zip', root_dir=ROOT_TEMP):
    with open(os.path.join(root_dir, filename), "wb") as binary_file:
        binary_file.write(bytes)
    return

def save_zip_file(zipfile, timestamp: str, extension: str ='.zip', root_dir: str = ROOT_TEMP):
    save_filename = f"{timestamp}-{zipfile.name}{extension}"
    zipfile_dir = os.path.join(root_dir, save_filename)

    FileSystemStorage(location=root_dir).save(save_filename, zipfile)     
    return zipfile_dir

@csrf_exempt
def login_api(request):
    body = request.body
    data = json.loads(body)

    username = data["username"]
    password = data["password"]
    user = authenticate(request, username=username, password=password)
    
    print(' --- 1: ', data)
    print(' --- login api(): ', username, password, type(data))

    response_data = {
        "is_authenticated": False, 
        "username": username, 
        "token": uuid.uuid4(), 
    }

    print(' --- 2: ', response_data['token'].is_safe)    
    request.session._get_or_create_session_key()
    print(' --- 3: ', request.session.session_key)

    if user is not None or request.user.is_authenticated:
        login(request, user)
        response_data['is_authenticated'] = True
        return JsonResponse(response_data)
    
    return JsonResponse(response_data)

@csrf_exempt
def upload_dataset_api(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'only POST is accepted'})
    
    body = request.body
    # data = json.loads(body)
    
    # print(body)
    print(' - session key ', request.session._get_or_create_session_key()) # rae4vk5d4ajdrd8x0gx6w7gemr4b5424
    
    headers = request.headers
    # token = headers['token']

    # if token == request.session['token']:
        # print(' - request.session token matches the user token')

    # name = data["name"]
    # ispublic = data["ispublic"]

    files = request.FILES
    zip_bytes_file = files['zip_bytes_file']
    timestamp = now_Ymd_HMS()
    save_zip_file(zip_bytes_file, timestamp) 

    # print(' --- login api(): ', name)

    response_data = {
        'upload_dataset_api function used': 'yes',
    }

    return JsonResponse(response_data)
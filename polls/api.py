from django.contrib.auth import authenticate, login, logout

def login_api(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    print(' --- login api() ', username, password)

    if user is not None or request.user.is_authenticated:
        login(request, user)
        return request
    
    return request

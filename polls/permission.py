from rest_framework import permissions
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        
        headers = request.headers
        token = headers.get('token')
        token_ = None
        username = request.POST.get('username')

        user = User.objects.get(username=username)
        if user != None:
            token_, created = Token.objects.get_or_create(user=user)

        if (obj.user == user and token == token_):
            "Allow permissions for methods on object."
            return True

        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user
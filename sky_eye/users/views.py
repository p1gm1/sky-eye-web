"""Users views."""

# Django REST
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from sky_eye.users.permissions import IsAccountOwner

# Serializer
from sky_eye.users.serializers import (
    UserLoginSerializer,
    UserModelSerializer,
    UserSignUpSerializer,
    AccountVerificationSerializer,
)

# Models
from sky_eye.users.models import User

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """User viewset.
    
    Handle signup, login and account verification.
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserModelSerializer
    lookup_field = 'username'

    def get_permissions(self):
        """Assign permissions based on actions."""

        if self.action in ['signup', 'login', 'verify']:
            permissions = [AllowAny]
        elif self.action in ['retrive', 'update', 'partial_update', 'destroy']:
            permissions = [IsAuthenticated, IsAccountOwner]
        else:
            permissions = [IsAuthenticated]

        return [p() for p in permissions]

    @action(detail=False, methods=['post'])
    def signup(self, request):
        """User signup."""

        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login."""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        user, token = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """User count verification."""
        serializer = AccountVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'message': 'Felicitaciones, ahora eres parte de la experiencia AiSky'}

        return Response(data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """Destroy user"""
        token = Token.objects.get(user=self.get_object())
        token.delete()
        return super().destroy(request, *args, **kwargs)
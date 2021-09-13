from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .serializers import UserRegisterSerializer, UserLoginSerializer, RefreshAuthTokenSerializer
from .services.authentication_rules import get_auth_tokens_lifetime
from .services.base_auth import authenticate_user, logout_user, refresh_access_token

User = get_user_model()


class RegisterUser(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUser(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        login_serializer = UserLoginSerializer(data=request.data)

        if login_serializer.is_valid():
            authenticated_user = authenticate_user(request.data.get('username'))

            return Response(authenticated_user, status=authenticated_user['status'])

        return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutUser(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout_serializer = RefreshAuthTokenSerializer(data=request.data)
        if logout_serializer.is_valid():
            refresh_auth_token = request.data.get('refresh_token')

            logged_out_user = logout_user(request, refresh_auth_token)

            return Response(logged_out_user, status=logged_out_user['status'])

        return Response(logout_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshAuthToken(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        login_serializer = RefreshAuthTokenSerializer(data=request.data)

        if login_serializer.is_valid():
            refresh_auth_token = request.data.get('refresh_token')
            authenticated_user = refresh_access_token(request, refresh_auth_token)

            return Response(authenticated_user, status=authenticated_user['status'])

        return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthTokensLifetime(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        tokens_lifetime = get_auth_tokens_lifetime()

        return Response(tokens_lifetime, status=status.HTTP_200_OK)

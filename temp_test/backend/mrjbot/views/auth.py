from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from ..serializers import (
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
)

User = get_user_model()


class AuthViewSet(viewsets.ViewSet):
    """ViewSet for authentication."""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user."""
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login a user."""
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'error': _('Please provide both username and password.')
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({
            'error': _('Invalid credentials.')
        }, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout a user."""
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': _('Successfully logged out.')})
        except Exception:
            return Response({'error': _('Invalid token.')}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """Get user profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update user profile."""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change user password."""
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'error': _('Invalid old password.')
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'detail': _('Password successfully changed.')})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
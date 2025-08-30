from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from django.utils import timezone

from .models import User, UserProfile, AuditLog
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer
)


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def log_user_action(user, action_type, description, request):
    """Log user action for audit trail"""
    AuditLog.objects.create(
        user=user,
        action_type=action_type,
        action_description=description,
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        
        log_user_action(
            user, 
            'login', 
            'User registered and logged in',
            request
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        tokens = get_tokens_for_user(user)
        
        log_user_action(
            user,
            'login',
            'User logged in successfully',
            request
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """User logout endpoint"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        log_user_action(
            request.user,
            'logout',
            'User logged out successfully',
            request
        )
        
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for user profile management"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        
        log_user_action(
            request.user,
            'data_modify',
            'User profile updated',
            request
        )
        
        return response


class UserDetailView(generics.RetrieveUpdateAPIView):
    """View for user details management"""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        
        log_user_action(
            request.user,
            'data_modify',
            'User details updated',
            request
        )
        
        return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password endpoint"""
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        
        log_user_action(
            request.user,
            'admin_action',
            'Password changed successfully',
            request
        )
        
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions(request):
    """Get user permissions and capabilities"""
    user = request.user
    
    permissions = {
        'can_access_emr': user.user_type in ['provider', 'admin'],
        'can_prescribe': user.user_type == 'provider',
        'can_use_zoom': user.can_use_zoom,
        'can_export_data': user.subscription_tier in ['premium', 'enterprise'],
        'is_admin': user.user_type == 'admin',
        'subscription_tier': user.subscription_tier,
        'user_type': user.user_type,
    }
    
    return Response(permissions, status=status.HTTP_200_OK)
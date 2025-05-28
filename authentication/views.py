from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import SignupSerializer, LoginSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
import secrets
import string


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    if request.method == 'POST':
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'status': 'success',
                'message': 'User created successfully.',
                'data': {
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'team': {
                            'id': user.team.id,
                            'name': user.team.name,
                            'role': user.team_role
                        }
                    }
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'message': 'Invalid data provided.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'status': 'success',
            'message': 'Login successful.',
            'data': {
                'token': token.key,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'team': {
                        'id': user.team.id,
                        'name': user.team.name,
                        'role': user.team_role
                    }
                }
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'status': 'error',
        'message': 'Invalid credentials.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    if request.method == 'POST':
        try:
            request.auth.delete()  # Delete the token
            return Response({
                'status': 'success',
                'message': 'Logged out successfully.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error during logout.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_account(request):
    try:
        user = request.user
        user.delete()
        return Response({
            'status': 'success',
            'message': 'Account deleted successfully.'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': 'Error deleting account.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_random_password():
    length = 12
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for i in range(length))

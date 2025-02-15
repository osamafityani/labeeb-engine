import random

from rest_framework.response import Response
from rest_framework import status

from .emails import send_otp_via_email
from .models import CustomUser
from .serializers import SignupSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from profiles import emails
import secrets
import string


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    if request.method == 'POST':
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            otp = random.randint(1000, 9999)
            user.otp = otp
            user.save()
            send_otp_via_email(user.email, otp)

            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key,
                             'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key, 'user_id': user.id}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    if request.method == 'POST':
        request.auth.delete()  # Delete the token
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user
    user.delete()


@api_view(['POST'])
def reset_password(request):
    try:
        try:
            email = request.data.get('email')
            new_password = request.data.get('new_password')
            user = CustomUser.objects.get(email=email)
        except:
            return Response("No user associated with this email", status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response("Reset password email sent successfully", status=status.HTTP_200_OK)
    except:
        return Response("We are having issues, try again later.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def verify_otp(request):
    try:
        otp = request.data.get('otp')
        user = request.user
        if user.otp != otp:
            return Response({'status': status.HTTP_400_BAD_REQUEST,
                             'message': 'Wrong otp'})

        user.is_verified = True
        user.save()
        return Response({'status': status.HTTP_200_OK,
                         'message': 'account_verified',
                         'data': {}})
    except:
        return Response({'status': status.HTTP_400_BAD_REQUEST,
                         'message': 'something went wrong'})


def generate_random_password():
    length = 12  # change the length as needed

    # Combine letters (both uppercase and lowercase), digits, and symbols
    characters = string.ascii_letters + string.digits

    # Generate a random password
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password

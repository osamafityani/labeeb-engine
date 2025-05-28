from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser
from teams.models import Team


class SignupSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(max_length=154, write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name', 'referral_code']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('referral_code', None)  # Remove referral code if present
        
        # Create a team for the user
        team = Team.objects.create(
            name=f"{validated_data['first_name']}'s Team",
            company=None
        )
        
        # Create the user with the team
        user = CustomUser.objects.create(
            **validated_data,
            team=team,
            team_role='owner'  # Set as team owner
        )
        user.set_password(password)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is not active.')
            else:
                raise serializers.ValidationError('Invalid credentials.')
        else:
            raise serializers.ValidationError('Email and password are required.')

        data['user'] = user
        return data

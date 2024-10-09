from rest_framework import serializers
from .models import User
from rest_framework.validators import UniqueValidator


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(
        ), message="A user with this email already exists.")]
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name',
                  'last_name']
        extra_kwargs = {
            'password': {'write_only': True},  # Make password write-only
        }

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')

        # Use the custom user manager's method to create a user with a new organization
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        return user

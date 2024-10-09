from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.views import APIView, Response
from rest_framework import status
from .serializers import UserRegisterSerializer


class UserRegisterView(APIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        '''
        Register a new user
        Expected data:
        {
            "email": "user@example.com",
            "password": "password",
            "first_name": "John",
            "last_name": "Doe"
        }
        '''
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

        @classmethod
        def get_token(cls, user):
            token = super().get_token(user)

            # Add custom claims to the token (e.g., user's name or any other field)
            token['email'] = user.email
            token['first_name'] = user.first_name
            token['last_name'] = user.last_name

            return token
    serializer_class = CustomTokenObtainPairSerializer

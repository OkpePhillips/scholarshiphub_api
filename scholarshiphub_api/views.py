from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from .models import User
from .serializers import UserSerializer, LoginSerializer
from .utils import send_verification_email

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
                else:
                    return Response({"Error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"Error": "No user found for the email provided"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def get(self, request, uid, token):
        try:
            user = User.objects.get(id=uid)
        except User.DoesNotExist:
            return Response({"detail": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            return Response({"detail": "Email verified successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
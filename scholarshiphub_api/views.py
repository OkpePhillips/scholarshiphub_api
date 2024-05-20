from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from rest_framework.authtoken.models import Token
from .models import User
from .serializers import UserSerializer, LoginSerializer
from .utils import send_verification_email
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
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
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
                else:
                    return Response({"Error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"Error": "No user found for the email provided"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"Message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            return Response({"Error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from rest_framework.authtoken.models import Token
from .models import User, Scholarship, Comment, StatementOfPurpose
from .serializers import UserSerializer, LoginSerializer, ScholarshipSerializer, CommentSerializer, StatementOfPurposeSerializer, UserEditSerializer, ScholarshipEditSerializer, CommentEditSerializer, StatementOfPurposeEditSerializer
from .utils import send_verification_email
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import permissions


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
    permission_classes = [permissions.IsAuthenticated]

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

class ScholarshipCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = ScholarshipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StatementOfPurposeCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = StatementOfPurposeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetScholarship(APIView):
    def get(self, request, id=None):     
        if id is not None:
            scholarships = Scholarship.objects.filter(id=id)
            if not scholarships.exists():
                return Response({"error": "scholarship not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            scholarships = Scholarship.objects.all()

        serializer = ScholarshipSerializer(scholarships, many=True)

        return Response(serializer.data)


class GetComments(APIView):
    def get(self, request, id=None):     
        if id is not None:
            comments = Comment.objects.filter(id=id)
            if not comments.exists():
                return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            comments = Comment.objects.all()

        serializer = CommentSerializer(comments, many=True)

        return Response(serializer.data)


class GetSOP(APIView):
    def get(self, request, id):     
        sop = Comment.objects.filter(id=id)
        serializer = StatementOfPurposeSerializer(sop)
        return Response(serializer.data)


class UserEditView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = UserEditSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScholarshipEditView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request):
        serializer = ScholarshipEditSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentEditView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, comment_id):
        try:
            return Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return None

    def put(self, request, comment_id):
        comment = self.get_object(comment_id)
        if comment is None:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        if comment.user != request.user:
            return Response({"error": "You do not have permission to edit this comment."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentEditSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StatementOfPurposeEditView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, sop_id):
        try:
            return StatementOfPurpose.objects.get(pk=sop_id)
        except StatementOfPurpose.DoesNotExist:
            return None

    def put(self, request, sop_id):
        sop = self.get_object(sop_id)
        if sop is None:
            return Response({"error": "SOP not found."}, status=status.HTTP_404_NOT_FOUND)

        if sop.user != request.user:
            return Response({"error": "You do not have permission to edit this SOP."}, status=status.HTTP_403_FORBIDDEN)

        serializer = StatementOfPurposeEditSerializer(sop, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_va5lid():
            user = request.user
            old_password = serializer.data.get("old_password")
            new_password = serializer.data.get("new_password")

            if not user.check_password(old_password):
                return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            return Response({"success": "Password changed successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


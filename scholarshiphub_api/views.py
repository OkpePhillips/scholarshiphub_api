from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from rest_framework.authtoken.models import Token
from .models import User, Scholarship, Comment, StatementOfPurpose
from .serializers import UserSerializer, LoginSerializer, ScholarshipSerializer, CommentSerializer, StatementOfPurposeSerializer, UserEditSerializer, ScholarshipEditSerializer, CommentEditSerializer, StatementOfPurposeEditSerializer, ChangePasswordSerializer
from .utils import send_verification_email
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q


class RegisterView(APIView):
    """
    View to register a new user.
    """
    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="This endpoint allows a new user to register by providing a first_name, last_name, username, email, and password.",
        tags=["User Processes"],
        request_body=UserSerializer,
        responses={
            200: openapi.Response(
                description="Successfully registered user details",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "new_user",
                        "email": "new_user@example.com"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
                examples={
                    "application/json": {
                        "username": ["This field is required."],
                        "email": ["This field is required."],
                        "password": ["This field is required."]
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """View for managing user login"""
    @swagger_auto_schema(
        operation_summary="Validate user credentials and login user",
        operation_description="This endpoint validates user's email and password, and returns the user object along with a token.",
        tags=["User Processes"],
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Loggedin user details and token",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "new_user",
                        "email": "new_user@example.com"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
                examples={
                    "application/json": {
                        "email": ["This field is required."],
                        "password": ["This field is required."]
                    }
                }
            )
        }
    )
    def post(self, request):
        """ Endpoint to login a user after validating credentials """
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
    """ Endpoint to logout from the API """
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Logout a user",
        operation_description="This endpoint deletes the token of a logged in user, effectively logging them out",
        tags=["User Processes"],
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            200: openapi.Response(
                description="Successful",
            ),
            401: openapi.Response(
                description="Unauthorized",
            )
        }
    )
    def delete(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"Message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            return Response({"Error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    """ Endpoint to verify email of a registered user """
    @swagger_auto_schema(
        operation_summary="Verify user email with token",
        operation_description="This endpoint verifies the email provided by the user",
        tags=["User Processes"],
        responses={
            200: openapi.Response(
                description="Email verified successfully",
            ),
            400: openapi.Response(
                description="Invalid token provided",
            )
        }
    )
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
    """ View for scholarship creation """
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (FormParser, MultiPartParser)
    @swagger_auto_schema(
        operation_summary="Create a new scholarship",
        operation_description="This endpoint will be used by admin users to create new scholarship objects",
        tags=["Admin Processes"],
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('image', openapi.IN_FORM, description="Image file for the scholarship", type=openapi.TYPE_FILE, required=True),
        ],
        request_body=ScholarshipSerializer,
        responses={
            200: openapi.Response(
                description="Created scholarship",
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "MasterCard Scholarship for STEM",
                        "description": "Scholarship targeted at STEM professionals ..."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
                examples={
                    "application/json": {
                        "title": ["This field is required."],
                        "description": ["This field is required."],
                        "eligibility": ["This field is required."],
                        "benefit": ["This field is required."],
                        "field_of_study": ["This field is required."],
                        "deadline": ["This field is required."],
                        "link": ["This field is required."]
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = ScholarshipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Comment on a scholarship",
        operation_description="This endpoint allows a user to create a comment on a scholarship post by providing the scholarship_id",
        tags=["Comments"],
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True),
        ],
        request_body=CommentSerializer,
        responses={
            200: openapi.Response(
                description="Comment posted",
                examples={
                    "application/json": {
                        "id": 1,
                        "scholarship_id": 1,
                        "content": "This scholarship has helped thousands of students. I am proud to have benefitted from it."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
                examples={
                    "application/json": {
                        "scholarship_id": ["This field is required."],
                        "content": ["This field is required."],
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StatementOfPurposeCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="Submit a request for Statement of Purpose",
        operation_description="This endpoint allows a user to request for review of their Statement of Purpose by submitting their draft",
        tags=["Statement of Purpose"],
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('title', openapi.IN_FORM, description="Description of the SOP", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('sop_file', openapi.IN_FORM, description="Statement of Purpose file", type=openapi.TYPE_FILE, required=True),
        ],
        responses={
            200: openapi.Response(
                description="Request submitted successfully"),
            400: openapi.Response(
                description="Bad Request - validation errors",
            )
        }
    )
    def post(self, request):
        serializer = StatementOfPurposeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetScholarship(APIView):
    """ View for retrieving scholarship objects """
    @swagger_auto_schema(
        operation_summary="Retrieve all scholarships",
        operation_description="This endpoint retrieves all scholarships from the database",
        tags=["Scholarships"],
        responses={
            200: openapi.Response(
                description="Successful",
                schema=ScholarshipSerializer(many=True),
            ),
            404: openapi.Response(
                description="No scholarship found",
            ),
        }
    )
    def get(self, request):
        scholarships = Scholarship.objects.all()
        serializer = ScholarshipSerializer(scholarships, many=True)
        return Response(serializer.data)

class GetAScholarship(APIView):
    """ Retrieve a specific scholarship based on id """
    @swagger_auto_schema(
        operation_summary="Retrieve a specific scholarship by ID",
        operation_description="This endpoint retrieves a specific scholarship from the database by its ID",
        tags=["Scholarships"],
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the scholarship to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful",
                schema=ScholarshipSerializer(),
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
            ),
            404: openapi.Response(
                description="Scholarship not found",
            ),
        }
    )
    def get(self, request, id):
        try:
            scholarship = Scholarship.objects.get(id=id)
            serializer = ScholarshipSerializer(scholarship)
            return Response(serializer.data)
        except Scholarship.DoesNotExist:
            return Response({"error": "Scholarship not found."}, status=status.HTTP_404_NOT_FOUND)


class GetComments(APIView):
    """ View to retrieve a comment """
    @swagger_auto_schema(
        operation_summary="Retrieve all comments",
        operation_description="This endpoint retrieves all comments from the database",
        tags=["Comments"],
        responses={
            200: openapi.Response(
                description="Request submitted successfully",
                schema=CommentSerializer(many=True),
            ),
            404: openapi.Response(
                description="Not found",
            ),
        }
    )
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

class GetAComment(APIView):
    """ Retrieve a specific comment by id """
    @swagger_auto_schema(
        operation_summary="Retrieve a specific comment by ID",
        operation_description="This endpoint retrieves a specific comment from the database by its ID",
        tags=["Comments"],
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the comment to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful",
                schema=CommentSerializer(),
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
            ),
            404: openapi.Response(
                description="Comment not found",
            ),
        }
    )
    def get(self, request, id):
        try:
            comment = Comment.objects.get(id=id)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)


class GetSOP(APIView):
    """ Retrieve an SOP object """
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Retrieve StatementOfPurpose objects from the database",
        operation_description="This endpoint retrieves a specific SOP from the database using an ID",
        tags=["Statement of Purpose"],
        manual_parameters=[
           openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the SOP to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True,
           ),
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful",
                schema=StatementOfPurposeSerializer(),
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
            ),
            404: openapi.Response(
                description="SOP not found",
            ),
        }
    )
    def get(self, request, id):     
        sop = StatementOfPurpose.objects.filter(id=id)
        serializer = StatementOfPurposeSerializer(sop)
        return Response(serializer.data)


class UserEditView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Edit a user profile details",
        operation_description="This endpoint allows a user to edit their profile details. However,email cannot be edited",
        tags=["User Processes"],
        request_body=UserEditSerializer,
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            200: openapi.Response(
                description="Edited user details",
                examples={
                    "application/json": {
                        "id": 1,
                        "first_name": "Lagbaja",
                        "last_name": "Tamedu",
                        "username": "wahala",
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
                examples={
                    "application/json": {
                        "first_name": ["This field is required."],
                        "last_name": ["This field is required."],
                    }
                }
            )
        }
    )
    def put(self, request):
        serializer = UserEditSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScholarshipEditView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary="Edit a scholarship post",
        operation_description="This endpoint will be used by admin users to edit a scholarship object",
        tags=["Admin Processes"],
        request_body=ScholarshipEditSerializer,
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            200: openapi.Response(
                description="Successful",
                schema=ScholarshipEditSerializer(),
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
            )
        }
    )
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
    @swagger_auto_schema(
        operation_summary="Edit comment",
        operation_description="This endpoint retrieves a specific comment and then edits it's content",
        tags=["Comments"],
        manual_parameters=[
           openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the comment to edit",
                type=openapi.TYPE_INTEGER,
                required=True,
           ),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            200: openapi.Response(
                description="Successful",
                schema=CommentEditSerializer(),
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
            ),
            404: openapi.Response(
                description="Comment not found",
            ),
        }
    )
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
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self, id):
        try:
            return StatementOfPurpose.objects.get(pk=id)
        except StatementOfPurpose.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="Edit Statement of Purpose",
        operation_description="This endpoint retrieves a specific SOP and then edits it",
        tags=["Statement of Purpose"],
        manual_parameters=[
           openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the SOP to edit",
                type=openapi.TYPE_INTEGER,
                required=True,
           ),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True,
            ),
            openapi.Parameter('sop_file', openapi.IN_FORM, description="Statement of Purpose file", type=openapi.TYPE_FILE,required=True),
        ],
        responses={
            200: openapi.Response(
                description="Successful",
                schema=StatementOfPurposeEditSerializer(),
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
            ),
            404: openapi.Response(
                description="SOP not found",
            ),
        }
    )
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

    @swagger_auto_schema(
        operation_summary="Change Password",
        operation_description="This endpoint allows a user to change their password by providing the old password, along with the new password",
        tags=["User Processes"],
        request_body=ChangePasswordSerializer,
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            200: openapi.Response(
                description="Password changed successfully",
            ),
            400: openapi.Response(
                description="Bad Request - validation errors",
                examples={
                    "application/json": {
                        "old_password": ["This field is required."],
                        "new_password": ["This field is required."],
                    }
                }
            )
        }
    )
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


class ScholarshipSearchView(APIView):
    """ Search view """
    @swagger_auto_schema(
        operation_summary="Search Scholarships",
        operation_description="This endpoint allows a user to Search for scholarships by title, and other fields in the scholarship table",
        tags=["Search"],
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search query",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: ScholarshipSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('search', None)
        if query:
            queryset = Scholarship.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(eligibility__icontains=query) |
                Q(benefit__icontains=query) |
                Q(field_of_study__icontains=query) |
                Q(deadline__icontains=query)
            )
        else:
            queryset = Scholarship.objects.all()
        
        serializer = ScholarshipSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserListView(APIView):
    """ View to retrieve all users by the admin """
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary="Get All Users: Admin Only",
        operation_description="This endpoint allows the admin user to retrieve all users in the database",
        tags=["Admin Processes"],
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            200: openapi.Response(
                description="Successful",
                schema=UserSerializer(many=True),
            ),
            401: openapi.Response(
                description="Unauthorized",
            ),
        }
    )
    def get(self, request, *args, **kwargs):

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteUserView(APIView):
    """ View to delete a user by the admin """
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_summary="Delete a User: Admin Only",
        operation_description="This endpoint allows the admin user to delete a user in the database",
        tags=["Admin Processes"],
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            200: openapi.Response(
                description="User deleted successfully",
            ),
            401: openapi.Response(
                description="Unauthorized",
            ),
        }
    )
    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            raise Http404
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UploadReviewedSOPView(APIView):
    """View for an admin to upload a review sop file """
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self, id):
        try:
            return StatementOfPurpose.objects.get(id=id)
        except StatementOfPurpose.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_summary="Upload a reviewed SOP file: Admin Only",
        operation_description="This endpoint allows the admin user to upload a reviewed sop file so the user can download it",
        tags=["Admin Processes"],
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authentication token", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('reviewed_sop', openapi.IN_FORM, description="Reviewed Statement of Purpose file", type=openapi.TYPE_FILE, required=True),
        ],
        responses={
            200: openapi.Response(
                description="Reviewed sop uploaded",
            ),
            401: openapi.Response(
                description="Unauthorized",
            ),
        }
    )
    def put(self, request, sop_id):
        sop = self.get_object(sop_id)
        serializer = ReviewSOPSerializer(sop, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
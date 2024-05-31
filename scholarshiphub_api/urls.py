from django.urls import path
from .views import RegisterView, LoginView, VerifyEmailView, LogoutView, ScholarshipCreateView, CommentCreateView, StatementOfPurposeCreateView, GetScholarship, GetComments, GetSOP, StatementOfPurposeEditView, CommentEditView, ScholarshipEditView, UserEditView, ChangePasswordView, GetAComment, GetAScholarship, ScholarshipSearchView, UserListView, DeleteUserView, UploadReviewedSOPView

from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="ScholarshipHub API",
      default_version='v1',
      description="The Scholarshiphub API allows for creation of scholarship posts, user registration and login, commenting on scholarship posts, and request for review of statement of purpose",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="okpegodwinfather@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('swagger/<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-email/<int:uid>/<str:token>/',VerifyEmailView.as_view(), name='verify-email'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('scholarships/create', ScholarshipCreateView.as_view(), name='create-scholarship'),
    path('comments/create', CommentCreateView.as_view(), name='create-comment'),
    path('sop/create', StatementOfPurposeCreateView.as_view(), name='create-sop'),
    path('scholarships/', GetScholarship.as_view(), name='get-all-scholarships'),
    path('scholarships/<int:id>/', GetAScholarship.as_view(), name='get-scholarship'),
    path('comments/', GetComments.as_view(), name='get-scholarships'),
    path('comments/<int:id>/', GetAComment.as_view(), name='get-scholarships'),
    path('sop/<int:id>/', GetSOP.as_view(), name='get-sop'),
    path('profile/update', UserEditView.as_view(), name='edit-profile'),
    path('scholarships', ScholarshipEditView.as_view(), name='edit-scholarship'),
    path('comments', CommentEditView.as_view(), name='edit-comment'),
    path('sop/<int:id>', StatementOfPurposeEditView.as_view(), name='edit-sop'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('scholarships/search/', ScholarshipSearchView.as_view(), name='search'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:id>/', DeleteUserView.as_view(), name='delete-user'),
    path('sop/<int:id>/review/', UploadReviewedSOPView.as_view(), name='upload-reviewed-sop'),
]

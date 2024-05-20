from django.urls import path
from .views import RegisterView, LoginView, VerifyEmailView, LogoutView, ScholarshipCreateView, CommentCreateView, StatementOfPurposeCreateView, GetScholarship, GetComments, GetSOP, StatementOfPurposeEditView, CommentEditView, ScholarshipEditView, UserEditView, ChangePasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-email/<int:uid>/<str:token>/',VerifyEmailView.as_view(), name='verify-email'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('scholarships/create', ScholarshipCreateView.as_view(), name='create-scholarship'),
    path('comments/create', CommentCreateView.as_view(), name='create-comment'),
    path('sop/create', StatementOfPurposeCreateView.as_view(), name='create-sop'),
    path('scholarships/', GetScholarship.as_view(), name='get-scholarships'),
    path('scholarships/<int:id>/', GetScholarship.as_view(), name='get-scholarships'),
    path('comments/', GetComments.as_view(), name='get-scholarships'),
    path('comments/<int:id>/', GetComments.as_view(), name='get-scholarships'),
    path('sop/<int:id>/', GetSOP.as_view(), name='get-sop'),
    path('profile/update', UserEditView.as_view(), name='edit-profile'),
    path('scholarships', ScholarshipEditView.as_view(), name='edit-scholarship'),
    path('comments', CommentEditView.as_view(), name='edit-comment'),
    path('sop/<int:id>', StatementOfPurposeEditView.as_view(), name='edit-sop'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
]

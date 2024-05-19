from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password=None, **extra_fields):
        if not first_name:
            raise ValueError("First name cannot be empty")
        if not last_name:
            raise ValueError("Last name cannot be empty")
        if not email:
            raise ValueError("Email name cannot be empty")
        
        email = self.normalize_email(email)
        user = self.model(first_name=first_name, last_name=last_name, email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, first_name, last_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        return self.create_user(self, first_name, last_name, email, password, **extra_fields)


class User(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    is_verified = models.BooleanField(default=False) 

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    groups = models.ManyToManyField(Group, related_name='scholarshiphub_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='scholarshiphub_permissions')

    objects = UserManager()

class Scholarship(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=3000)
    eligibility = models.TextField(max_length=500)
    benefit = models.TextField(max_length=500)
    field_of_study = models.CharField(max_length=255)
    Deadline = models.CharField(max_length=500)
    link = models.CharField(max_length=500)
    image = models.ImageField(verbose_name="Scholarship Image", upload_to="scholarship_images/", null=True, blank=True)

class Comment(models.Model):
    scholarship = models.ForeignKey(Scholarship, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', related_name='replies', null=True, blank=True, on_delete=models.CASCADE)


class StatementOfPurpose(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sop_file = models.FileField(upload_to='sop_files/')
    submission_date = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_sop = models.FileField(upload_to='reviewed_sop/', null=True, blank=True)




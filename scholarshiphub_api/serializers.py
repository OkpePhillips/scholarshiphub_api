from rest_framework import serializers
from .models import User, Scholarship, Comment, StatementOfPurpose

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'is_verified']
    
    def create(self, validated_data):
        user = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user



class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = ['id', 'title', 'description', 'eligibility','benefit', 'field_of_study', 'deadline', 'link', 'image']


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    scholarship_id = serializers.PrimaryKeyRelatedField(queryset=Scholarship.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'username', 'user','content', 'parent_comment', 'replies', 'created_at', 'scholarship_id']
    
    def get_replies(self, obj):
        if obj.replies:
            return CommentSerializer(obj.replies.all(), many=True).data



class StatementOfPurposeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = StatementOfPurpose
        fields = ['user', 'title', 'sop_file', 'submission_date', 'is_reviewed', 'reviewed_sop']


class ReviewSOPSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatementOfPurpose
        fields = ['reviewed_sop', 'is_reviewed']

    def update(self, instance, validated_data):
        instance.reviewed_sop = validated_data.get('reviewed_sop', instance.reviewed_sop)
        instance.is_reviewed = True
        instance.save()
        return instance

class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class ScholarshipEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = ['title', 'description', 'eligibility','benefit', 'field_of_study', 'deadline', 'link', 'image']

class CommentEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']


class StatementOfPurposeEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatementOfPurpose
        fields = ['title', 'sop_file']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
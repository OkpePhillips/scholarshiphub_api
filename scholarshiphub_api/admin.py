from django.contrib import admin
from .models import User, Scholarship, Comment, StatementOfPurpose

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'username', 'is_verified', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_verified',)

class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'field_of_study', 'deadline')
    search_fields = ('title', 'field_of_study')
    list_filter = ('field_of_study',)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content', 'parent_comment', 'created_at')
    search_fields = ('user__email', 'content')
    list_filter = ('created_at',)

class StatementOfPurposeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'submission_date', 'is_reviewed')
    search_fields = ('user__email', 'title')
    list_filter = ('is_reviewed', 'submission_date')

admin.site.register(User, UserAdmin)
admin.site.register(Scholarship, ScholarshipAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(StatementOfPurpose, StatementOfPurposeAdmin)
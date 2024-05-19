from django.contrib import admin
from .models import User, Scholarship, Comment, StatementOfPurpose

admin.site.register(User)
admin.site.register(Scholarship)
admin.site.register(Comment)
admin.site.register(StatementOfPurpose)
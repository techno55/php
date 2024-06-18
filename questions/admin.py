from django.contrib import admin
from .models import User, Question, LearningHistory, Result

admin.site.register(User)
admin.site.register(Question)
admin.site.register(LearningHistory)
admin.site.register(Result)

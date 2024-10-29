from django.contrib import admin

from .models import Model, Dataset, Choice, Question


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"]}),
    ]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Model)

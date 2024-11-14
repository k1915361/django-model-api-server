from django.contrib import admin

from .models import Model, Dataset, ModelDataset, Choice, Question


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"]}),
    ]

admin.site.register(Model)
admin.site.register(Dataset)
admin.site.register(ModelDataset)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)


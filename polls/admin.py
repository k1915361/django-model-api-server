from django.contrib import admin

from .models import Model, Dataset, Image_Dataset, CSV_Dataset, Choice, Question


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"]}),
    ]

admin.site.register(Model)
admin.site.register(Dataset)
admin.site.register(CSV_Dataset)
admin.site.register(Image_Dataset)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)


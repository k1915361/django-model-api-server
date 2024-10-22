from django.contrib import admin

from .models import Question, Login, Net_Model, Choice


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"]}),
    ]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Login)
admin.site.register(Net_Model)
admin.site.register(Choice)

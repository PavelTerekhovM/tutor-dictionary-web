from django.contrib import admin
from .models import Lesson, Card


class LessonAdmin(admin.ModelAdmin):
    list_display = ('dictionary', 'student', 'required_answers', 'created')


admin.site.register(Lesson, LessonAdmin)


class CardAdmin(admin.ModelAdmin):
    list_display = (
        'word', 'lesson', 'created', 'correct_answers',
        'status', 'all_attempts', 'all_correct_answers', 'created'
    )


admin.site.register(Card, CardAdmin)

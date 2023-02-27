from django.urls import path
from .views import (
    change_number_answers,
    change_card_status,
    lesson,
    learn
)

app_name = 'lesson'

urlpatterns = [
    path(
        'change_number_answers/<int:user_pk>/'
        '<int:dictionary_pk>/<int:lesson_pk>/',
        change_number_answers,
        name='change_number_answers'
    ),
    path(
        'change_card_status/<int:user_pk>/'
        '<int:dictionary_pk>/<int:card_pk>/',
        change_card_status,
        name='change_card_status'
    ),
    path(
        'lesson/<int:user_pk>/<int:dictionary_pk>/',
        lesson,
        name='lesson'
    ),
    path(
        'learn/<int:translation_reverse>/<int:user_pk>/'
        '<int:dictionary_pk>/<int:card_pk>/',
        learn,
        name='learn'
    ),
]

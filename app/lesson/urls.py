from django.urls import path
from .views import (
    ChangeNumberAnswers,
    change_card_status,
    lesson,
    learn, LearnDetailView, LearnView
)

app_name = 'lesson'

urlpatterns = [
    path(
        'change_number_answers/',
        ChangeNumberAnswers.as_view(),
        name='change_number_answers'
    ),
    path(
        'change_card_status/',
        change_card_status,
        name='change_card_status'
    ),
    path(
        '<int:user_pk>/<int:dictionary_pk>/',
        lesson,
        name='lesson'
    ),
    path(
        'learn/<int:lesson_pk>/',
        LearnView.as_view(),
        name='learn'
    ),
    path(
        'learn/<str:reverse>/<int:lesson_pk>/',
        LearnView.as_view(),
        name='learn'
    ),
    path(
        'learn/<int:lesson_pk>/',
        learn,
        name='learn'
    ),
    path(
        'learn/<str:reverse>/<int:lesson_pk>/',
        learn,
        name='learn'
    ),
]

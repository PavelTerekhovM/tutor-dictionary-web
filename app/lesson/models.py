from django.contrib.auth.models import User
from django.db import models
from dictionary.models import Dictionary, Word
from django.urls import reverse
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
import random


class Lesson(models.Model):
    dictionary = models.ForeignKey(
        Dictionary,
        on_delete=models.CASCADE,
        related_name='dictionary'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student'
    )
    required_answers = models.IntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.dictionary.title

    def get_absolute_url(self):
        return reverse(
            'lesson:lesson',
            kwargs={
                'user_pk': self.student.pk,
                'dictionary_pk': self.dictionary.pk
            }
        )

    def get_random(self, card=None, visited=None):
        """
        The function handle chosing first and all next random
        cards in lesson
        :arg visited - pasing from view list of cards' ids
        visited within lesson
        """
        if not card:
            cards = Card.objects.filter(lesson=self).filter(status='active')
        else:
            card = Card.objects.get(pk=card.pk)
            # take card from lesson with answers less than current card
            cards = Card.objects.filter(lesson=self).\
                filter(status='active').\
                exclude(id__in=visited)
        if cards:
            next_card = random.choice(cards)
        else:
            next_card = None
        return next_card


class Card(models.Model):
    STATUS_CHOICES = (
        ('active', 'Учить'),
        ('done', 'Выучено'),
        ('disable', 'Отложено')
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name='word'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='lesson',
        null=True
    )
    created = models.DateTimeField(auto_now_add=True)
    correct_answers = models.IntegerField(default=0)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    all_attempts = models.IntegerField(default=0)
    all_correct_answers = models.IntegerField(default=0)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.word.body

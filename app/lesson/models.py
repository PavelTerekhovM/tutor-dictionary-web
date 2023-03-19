from django.conf import settings
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
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
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

    def create_cards(self):
        """
        Creating new cards when lesson first time rendered
        """
        for word in self.dictionary.word.all():
            Card.objects.get_or_create(word=word, lesson=self)

    def get_active_cards(self):
        """
        The function ruturns QuerySet of all active cards
        """
        qs = Card.objects.filter(lesson=self)\
            .filter(status='active')\
            .select_related('word')
        return qs

    def get_random(self, visited=None):
        """
        The function returns random not visited card
        """
        if not visited:
            visited = []
        else:
            visited = visited[:]
        cards = self.get_active_cards().exclude(id__in=visited)
        if len(cards) > 1:
            return random.choice(cards), True
        elif len(cards) > 0:
            return random.choice(cards), False
        return None, False

    def get_next(self, card, visited=None):
        """
        The function returns True if there is unvisited cards or False
        """
        if not visited:
            visited = []
        else:
            visited = visited[:]
        visited.append(card.pk)
        qs = self.get_active_cards().exclude(id__in=visited).count()
        return qs != 0


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

    def change_status(self, new_status):
        """
        Method to change card status and required number of answers:
        - 'active' -> 'done': change number of answers to required in lesson
        - 'done' -> 'active': change to zero
        """
        if new_status == 'done':
            self.correct_answers = self.lesson.required_answers
        elif self.status == 'done' and new_status == 'active':
            self.correct_answers = 0
        self.status = new_status
        self.save()

    def check_card(self, answer, reverse):
        """
        Method checks answers, changes stats appropriately:
        """
        self.all_attempts += 1
        if reverse == 'reverse':
            question = self.word.translations.lower()
        else:
            question = self.word.body.lower()
        chars = (",", ";", "...", "|", "\n", "\t", "n‘", "n’",
                 'n"', "n'", "‘", "’", '"', '  ', '   ', "'")
        for char in chars:
            answer = answer.replace(char, " ")
            question = question.replace(char, " ")
        if len(answer) != 0 and answer in question:
            self.correct_answers += 1
            self.all_correct_answers += 1
            if self.correct_answers == self.lesson.required_answers:
                self.status = 'done'
            self.save()
            status, msg = 'success', 'Это верный ответ'
        else:
            status, msg = 'danger', 'Это неверный ответ'
        self.save()
        return status, msg

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models import Q
from django.urls import reverse


class DetailManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()\
            .select_related('author')\
            .prefetch_related('student')\
            .prefetch_related('word')

    def get_available(self, user):
        """
        Getting queryset of all public dictionaries
        where user is not author or student
        For anonymous user return all public dictionaries
        """
        qs = self.get_queryset().filter(status="public")
        if not isinstance(user, AnonymousUser):
            qs = qs.exclude(student=user).exclude(author=user)
        return qs

    def get_my_dict(self, user):
        """
        Getting queryset of all dictionaries
        where user is author or student
        """
        return self.filter(
            Q(author=user) | (Q(student=user) & Q(status='public'))
        )


class Dictionary(models.Model):
    STATUS_CHOICES = (
        ('private', 'Private'),
        ('public', 'Public'),
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    student = models.ManyToManyField(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='private'
    )
    word = models.ManyToManyField('Word')
    note = models.CharField(max_length=500)
    file = models.FileField(upload_to='file/%Y/%m/%d/')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='creator_of_dictionary'
    )

    objects = models.Manager()
    detail_objects = DetailManager()

    class Meta:
        ordering = ('title',)
        verbose_name = 'Словарь'
        verbose_name_plural = 'Словари'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'dictionary:dictionary_detail',
            kwargs={'pk': self.pk}
        )


class Word(models.Model):
    body = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    translations = models.CharField(max_length=250)
    example = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('body',)
        index_together = (('id', 'slug'),)
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'

    def __str__(self):
        return self.body

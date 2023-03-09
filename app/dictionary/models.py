from django.conf import settings
from django.db import models
from django.urls import reverse


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

    class Meta:
        ordering = ('title',)
        verbose_name = 'Словарь'
        verbose_name_plural = 'Словари'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'dictionary:dictionary_detail',
            kwargs={'slug': self.slug, 'pk': self.pk}
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

from django.contrib import messages
from django.shortcuts import redirect

from lesson.models import Lesson
from .models import Dictionary
from django.http import HttpResponseBadRequest


def ajax_required(f):
    def wrap(request, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def author_required(f):
    def wrap(request, *args, **kwargs):
        dictionary_pk = request.POST.get('dictionary_pk')
        author = Dictionary.objects.get(pk=dictionary_pk).author
        if author != request.user:
            messages.error(
                request,
                'Вы не являетесь автором этого словаря. '
                'Вы можете скачать фаил и добавить его в свои словари.'
            )
            return redirect('lesson:lesson', request.user.pk, dictionary_pk)
        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def available_for_learning(f):
    """
    Decorator checks if dictionary is public or user is its author
    """
    def wrap(request, *args, **kwargs):
        dictionary_pk = kwargs.get('dictionary_pk')
        lesson_pk = kwargs.get('lesson_pk')
        if dictionary_pk:
            dictionary = Dictionary.objects\
                .select_related('author')\
                .get(pk=dictionary_pk)
        else:
            dictionary = Lesson.objects\
                .select_related('dictionary', 'dictionary__author')\
                .get(pk=lesson_pk).dictionary
        if not (
            (
                request.user == dictionary.author
            ) or (
                dictionary.status == 'public'
            )
        ):
            messages.error(request, 'Автор словаря ограничил доступ к нему')
            return redirect('dictionary:my_dictionaries')
        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap

from django.contrib import messages
from django.shortcuts import redirect
from .models import Dictionary


def author_required(f):
    def wrap(request, *args, **kwargs):
        pk = request.POST.get('dictionary_pk')
        author = Dictionary.objects.get(pk=pk).author
        if author != request.user:
            messages.error(
                request,
                'Вы не являетесь автором этого словаря. '
                'Вы можете скачать фаил и добавить его в свои словари.'
            )
            return redirect('dictionary: dictionary_detail', pk)
        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def available_for_learning(f):
    """
    decorators allow to render dictionary in
    lesson and learning only for author and
    student if dictionary is public
    """
    def wrap(request, *args, **kwargs):
        pk = kwargs['dictionary_pk']
        if not (
            (
                request.user == Dictionary.objects.get(pk=pk).author
            ) or (
                Dictionary.objects.get(pk=pk).status == 'public'
            )
        ):
            messages.error(request, 'Автор словаря ограничил доступ к нему')
            return redirect('my_dictionaries')
        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap

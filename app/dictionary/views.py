from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import ListView, DetailView, CreateView

from dictionary.decorators import author_required
from dictionary.forms import AddStudentForm, DictionaryForm, SearchForm
from dictionary.models import Dictionary


@login_required
@require_POST
def student_add(request, pk, **kwargs):
    """
    Function adds a current user to the list of
    student and redirect to lesson detail.
    """
    dictionary = get_object_or_404(Dictionary, pk=pk)
    user = request.user
    form = AddStudentForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        dictionary.student.add(user)
        messages.success(request, 'Вы успешно добавили словарь')
    else:
        messages.error(request, 'Что-то пошло не так, повторите попытку')
    return redirect('lesson:lesson', user.pk, pk)


@login_required
@require_GET
def student_remove(request, slug, pk):
    """
    Function removes a current user from the list of
    student and redirect to dictionary detail back.
    """
    dictionary = get_object_or_404(Dictionary, pk=pk)
    user = request.user
    try:
        dictionary.student.remove(user)
    except:
        messages.error(request, 'Что-то пошло не так, повторите попытку')
    else:
        messages.success(request, 'Вы успешно удалили словарь')
    return redirect('dictionary_detail', slug, pk)


@author_required
def make_private(request, pk, **kwargs):
    """
    Function makes the dictionary private, which means
    visible and available only its author.
    """
    dictionary = get_object_or_404(Dictionary, pk=pk)
    user = request.user
    try:
        dictionary.status = 'private'
        dictionary.save()
    except:
        messages.error(request, 'Что-то пошло не так, повторите попытку')
    else:
        messages.success(request, 'Вы успешно сделали словарь приватным')
    return redirect('lesson:lesson', user.pk, pk)


@author_required
def make_public(request, pk, **kwargs):
    """
    Function makes the dictionary public,
    which means visible and available all users.
    """
    dictionary = get_object_or_404(Dictionary, pk=pk)
    user = request.user
    try:
        dictionary.status = 'public'
        dictionary.save()
    except:
        messages.error(request, 'Что-то пошло не так, повторите попытку')
    else:
        messages.success(request, 'Вы успешно сделали словарь общидоступным')
    return redirect('lesson:lesson', user.pk, pk)


@author_required
def dictionary_delete(request, pk, **kwargs):
    """
    Function deletes the dictionary and redirect
    user to the list of dictionaries
    """
    dictionary = get_object_or_404(Dictionary, pk=pk)
    try:
        dictionary.delete()
    except:
        messages.error(request, 'Что-то пошло не так, повторите попытку')
    else:
        messages.success(request, 'Вы успешно удалили словарь')
    return redirect('my_dictionaries')


class Dictionary_list(ListView):
    """
    view makes list all public dictionaries, then
    template additionally excludes dictionaries where
    the user is in the student list or author
    """
    model = Dictionary
    paginate_by = 1

    queryset = Dictionary.objects.filter(status="public").\
        select_related('author')\
        .prefetch_related('word')

    template_name = "dictionary/list.html"
    context_object_name = 'dictionaries'


class My_dictionary_list(LoginRequiredMixin, ListView):
    model = Dictionary
    paginate_by = 1
    template_name = "dictionary/my_dictionaries.html"
    context_object_name = 'dictionaries'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            Q(
                author=self.request.user
            ) | (Q(
                student=self.request.user
            ) & Q(
                status='public'
            ))
        ).select_related('author').prefetch_related('word')


class Dictionary_detail(DetailView):
    model = Dictionary
    student_add_form = AddStudentForm
    template_name = "dictionary/detail.html"
    context_object_name = 'dictionary'
    queryset = Dictionary.objects.all().\
        select_related('author').\
        prefetch_related('word')


class AddDictionaryView(LoginRequiredMixin, CreateView):
    """
    form.save() handling creating all objects required to
    create new dictionary
    """
    form_class = DictionaryForm
    template_name = 'dictionary/upload_file.html'
    success_url = reverse_lazy('dictionary:my_dictionaries')

    def get_initial(self):
        """
        Placing request.user to initial dictionary to make it
        available while saving form
        """
        super().get_initial()
        self.initial.update({'author': self.request.user})
        return self.initial

    def form_valid(self, form):
        """
        in case of exceptions while parsing file we redirect back
        with error message
        """
        self.object = form.save()
        if not self.object:
            messages.error(
                self.request,
                'Что-то пошло не так, повторите попытку'
            )
            return redirect('upload_file')
        return HttpResponseRedirect(self.get_success_url())


def dictionary_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Dictionary.objects.filter(
                Q(author=request.user.id) | (Q(status='public'))).\
                filter(
                Q(
                    title__icontains=query
                ) | (Q(
                    word__body__icontains=query
                )) | (Q(
                    word__translations__icontains=query
                ))
            ).distinct()
    return render(request, 'dictionary/search.html',
                  {'form': form, 'query': query, 'results': results})

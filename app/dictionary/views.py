import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import FormMixin
from django.db.models import Q

from dictionary.decorators import author_required, ajax_required
from dictionary.forms import (
    ChoiceDictionaryForm,
    DictionaryForm,
    SearchForm
)
from dictionary.models import Dictionary


@login_required
@require_POST
def add_dictionary(request):
    """
    Function to add dictionary to my_dictionary
    """
    dictionary_pk = request.POST.get('dictionary_pk')
    dictionary = get_object_or_404(Dictionary, pk=dictionary_pk)
    user = request.user
    form = ChoiceDictionaryForm(request.POST)
    if form.is_valid():
        dictionary.student.add(user)
        messages.success(request, 'Вы успешно добавили словарь')
    else:
        messages.error(request, 'Что-то пошло не так, повторите попытку')
    return redirect('lesson:lesson', user.pk, dictionary_pk)


@login_required
@require_POST
def remove_dictionary(request):
    """
    Function to remove dictionary from my_dictionary
    """
    dictionary_pk = request.POST.get('dictionary_pk')
    dictionary = get_object_or_404(Dictionary, pk=dictionary_pk)
    user = request.user
    form = ChoiceDictionaryForm(request.POST)
    if form.is_valid():
        dictionary.student.remove(user)
        messages.success(request, 'Словарь удален из ваших словарей')
    else:
        messages.error(request, 'Что-то пошло не так, повторите попытку')
    return redirect('dictionary:dictionary_detail', dictionary_pk)


@login_required
@require_POST
@ajax_required
@author_required
def change_status(request):
    """
    Function change status of dictionary
    - private ones available only its author
    - public ones available for all
    """
    dictionary_pk = request.POST.get('dictionary_pk')
    dictionary = get_object_or_404(Dictionary, pk=dictionary_pk)
    form = ChoiceDictionaryForm(request.POST)
    response_data = {}
    if form.is_valid():
        if dictionary.status == 'private':
            dictionary.status = 'public'
            dictionary.save()
        else:
            dictionary.status = 'private'
            dictionary.save()
        response_data['action_status'] = 'success'
        response_data['msg'] = 'Статус словаря успешно изменен'
    else:
        response_data['action_status'] = 'danger'
        response_data['msg'] = 'Что-то пошло не так, повторите попытку'

    response_data['dictionary_status'] = dictionary.status

    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json",
    )


@login_required
@require_POST
@author_required
def delete_dictionary(request):
    """
    Function deletes the dictionary and redirect
    user to the list of dictionaries
    """
    dictionary_pk = request.POST.get('dictionary_pk')
    dictionary = get_object_or_404(Dictionary, pk=dictionary_pk)
    form = ChoiceDictionaryForm(request.POST)
    if form.is_valid():
        dictionary.delete()
        messages.success(request, 'Вы успешно удалили словарь')
    else:
        messages.error(request, 'Что-то пошло не так, повторите попытку')
    return redirect('dictionary:my_dictionaries')


class Dictionary_list(ListView):
    """
    View render list all public dictionaries which user is not
    author or student
    """
    model = Dictionary
    paginate_by = 1
    template_name = "dictionary/list.html"
    context_object_name = 'dictionaries'

    def get_queryset(self):
        return Dictionary.detail_objects.get_available(self.request.user)


class My_dictionary_list(LoginRequiredMixin, ListView):
    model = Dictionary
    paginate_by = 1
    template_name = "dictionary/my_dictionaries.html"
    context_object_name = 'dictionaries'

    def get_queryset(self):
        return Dictionary.detail_objects.get_my_dict(self.request.user)


class Dictionary_detail(FormMixin, DetailView):
    """
    Class view to render detail view of dictionary
    AddStudentForm to add the dictionary for studing
    """
    form_class = ChoiceDictionaryForm
    template_name = "dictionary/detail.html"
    context_object_name = 'dictionary'
    queryset = Dictionary.detail_objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_form'] = ChoiceDictionaryForm(
            initial={'dictionary_pk': self.object.pk}
        )
        return context


class AddDictionaryView(LoginRequiredMixin, CreateView):
    """
    View which handling creating all objects required to
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
            return redirect('dictionary:upload_file')
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

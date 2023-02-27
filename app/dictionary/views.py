from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Dictionary, Word
from .forms import DictionaryForm, AddStudentForm, SearchForm
from django.urls import reverse_lazy
import xml.etree.ElementTree as ET
from django.template.defaultfilters import slugify
from .forms import UserRegistrationForm
from django.views.generic.edit import CreateView
from django.views.decorators.http import require_POST, require_GET
from .decorators import author_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages


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


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')
    form_class = UserRegistrationForm
    success_message = "Вы успешно зарегистрировались на сайте Lingvo tutor"


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
    form_class = DictionaryForm
    template_name = "dictionary/upload_file.html"
    success_url = reverse_lazy("my_dictionaries")

    def form_valid(self, form):
        """
        parse uploaded xml-file
        - take parts of file in for-cycle  and add them
        in byte-string
        - find title of dictionary-file, create a new
        instance of dictionary
        - parse byte-string and find all cards, take words,
        translations and examples
        - create new instance of words for each card
        - assign all new word instances to the created dictionary
        """
        form.instance.author = self.request.user
        uploaded_file = self.request.FILES['file']
        # can't read uploaded_file, so add all lines to byte-string
        file = b''
        for line in uploaded_file:
            file += line

        # parse file with ElementTree module
        tree = ET.ElementTree(ET.fromstring(file))
        root = tree.getroot()
        title = root.attrib['title']  # find name of file
        slug = slugify(title)
        form.instance.author = self.request.user
        form.instance.title = title
        form.instance.slug = slug
        self.object = form.save()

        # internal method recursively find all nodes
        for card in root.iter('card'):
            # need to clean variable from value of previous card
            example = ''
            for translations in card.iter('translations'):
                # find translation of word
                translations = translations.find('word').text
            for word in card.iter('word'):
                if word.attrib:
                    body = word.text        # find text of word
            for example in card.iter('example'):
                example = example.text      # find example of word

            slug = slugify(body)
            # create and save new word in DB
            new_word = Word.objects.create(
                body=body,
                slug=slug,
                translations=translations,
                example=example)

            new_word.save()
            self.object.word.add(new_word)
        self.object = form.save()
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


def about(request):
    return render(request, 'dictionary/about.html',)

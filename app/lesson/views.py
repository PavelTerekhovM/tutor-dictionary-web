from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core import serializers

from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View

from django.views.decorators.http import require_POST
from django.views.generic import FormView, DetailView
from django.views.generic.detail import SingleObjectMixin

from dictionary.decorators import available_for_learning
from dictionary.forms import ChoiceDictionaryForm

from lesson.forms import (
    ChangeNumberAnswersForm,
    ChangeCardStatus,
    LearnForm,
)
from lesson.models import Lesson, Card
from dictionary.models import Dictionary


class JSONResponseMixin:
    """
    Class responsible handling JSON response:
    - add specific context;
    - return response
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        No self.card means there is no content to serialise
        """
        if not self.card:
            return JsonResponse(context)

        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Method removes lesson, form and view as they don't need for
        rendering through AJAX
        """
        card = serializers.serialize("json", [self.card.word, ])
        context.pop('form')
        context['card'] = card
        context['card_pk'] = self.card.pk
        return context


class HTMLResponseMixin:
    """
    Class responsible for handling HTML response
    - add specific context and messages;
    - return response
    """
    def render_to_html_response(self, context):
        """
        No self.card means there is no content to retrive, therefore
        returning redirect with messages
        """
        if self.card:
            return super().render_to_response(
                self.get_html_data(context),
            )
        else:
            return redirect(
                'lesson:lesson',
                dictionary_pk=self.object.dictionary.pk,
                user_pk=self.request.user.pk
            )

    def get_html_data(self, context):
        """
        Method add data and messages to request before returning response
        """
        if context['status'] == 'success':
            messages.success(self.request, context['msg'])
        elif context['status'] == 'warning':
            messages.warning(self.request, context['msg'])
        else:
            messages.error(self.request, context['msg'])

        context['lesson'] = self.object
        context['card'] = self.card
        return context


class BaseLearnView(JSONResponseMixin, HTMLResponseMixin, SingleObjectMixin):
    """
    Base class for LearnView:
    - set common attrs for all methods;
    - prepare common context for both HTML and JSON responses
    - dispatch request to HTML and JSON responses
    """
    model = Lesson
    pk_url_kwarg = 'lesson_pk'
    template_name = 'learn.html'
    visited = []
    card = None
    next_card = None
    reverse = None

    def setup(self, request, *args, **kwargs):
        self.visited = request.session.setdefault('visited', [])
        self.reverse = kwargs.get('reverse', None)
        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Method prepares common context for both HTML and JSON responses
        """
        context = {
            'form': kwargs.get('form'),
            'status': kwargs.get('status'),
            'msg': kwargs.get('msg'),
            'reverse': self.reverse,
            'next_card': self.next_card,
        }
        return context

    def render_to_response(self, context):
        """
        Method dispatchs request to HTML and JSON responses
        """
        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return self.render_to_json_response(context)
        else:
            return self.render_to_html_response(context)


@method_decorator([available_for_learning, login_required], name='dispatch')
class LearnView(View):
    """
    Class responsible to distinguish GET and POST requests
    """
    def get(self, request, *args, **kwargs):
        view = LearnDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = LearnFormView.as_view()
        return view(request, *args, **kwargs)


class LearnFormView(BaseLearnView, FormView):
    """
    Class responsible for handling POST requests:
    - retriving answer from form;
    - call card.check_card() to check answer and change card data;
    - append checked card to visited;
    - call lesson.get_next() to retrieve next_card;
    - no next_card triggers flushing visited;
    """
    form_class = LearnForm

    def post(self, request, *args, **kwargs):
        self.card = get_object_or_404(
            Card.objects.select_related(
                'lesson',
                'word',
                'lesson__dictionary'
            ),
            pk=request.POST.get('card_pk')
        )
        self.object = self.card.lesson
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.visited.append(self.card.pk)
        cd = form.cleaned_data
        answer = cd['body'].lower() or cd['translations'].lower()
        status, msg = self.card.check_card(answer, self.reverse)
        self.next_card = self.object.get_next(self.card, self.visited)
        if not self.next_card:
            self.visited.clear()
        self.request.session.modified = True
        context = self.get_context_data(
            status=status,
            msg=msg,
            form=form,
        )
        return self.render_to_response(context)

    def form_invalid(self, form):
        status, msg = 'danger', 'Что-то пошло не так, повторите попытку'
        context = self.get_context_data(
            status=status,
            msg=msg,
            form=form,
        )
        return self.render_to_response(context)


class LearnDetailView(BaseLearnView, DetailView):
    """
    Class responsible for handling GET requests:
    - call lesson.get_random() to retrieve random and next cards;
    - no next_card triggers flushing visited;
    - no active_cards() triggers end of lesson and redirecting;
    - add to context form with initial;
    """
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.card, self.next_card = self.object.get_random(self.visited)
        if not self.card:
            self.visited.clear()
            request.session.modified = True
            if not self.object.get_active_cards():
                context = {
                    'status': 'danger',
                    'msg': 'В выбранном словаре нет активных карточек, '
                           'измените настройки словаря и попробуйте снова.'
                }
                return self.render_to_response(context)
        return self.render_to_response(context=self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = LearnForm(
            initial={
                'card_pk': self.card.pk,
            },
        )
        if self.reverse:
            field = form.fields['translations']
        else:
            field = form.fields['body']
        field.widget = field.hidden_widget()
        context['form'] = form
        return context


@login_required
@require_POST
def change_card_status(request):
    """
    The view process the form of changing status
    of cards
    """
    card_pk = request.POST.get('card_pk')
    back_url = request.POST.get('back_url')
    card = get_object_or_404(Card, pk=card_pk)
    form = ChangeCardStatus(request.POST)
    if form.is_valid():
        new_status = form.cleaned_data['status']
        card.change_status(new_status)
        messages.success(
            request,
            'Изменения внесены'
        )
    else:
        messages.error(
            request,
            'Что-то пошло не так, повторите попытку'
        )
    return redirect(back_url)


class ChangeNumberAnswers(LoginRequiredMixin, FormView):
    """
    The view process the form of changing required
    number of answers in the lesson and redirect back.
    """
    form_class = ChangeNumberAnswersForm
    http_method_names = ['post', ]

    def form_valid(self, form):
        lesson_pk = self.request.POST.get('lesson_pk')
        current_lesson = get_object_or_404(
            Lesson,
            pk=lesson_pk
        )
        cd = form.cleaned_data
        current_lesson.required_answers = cd['required_answers']
        current_lesson.save()
        response_data = {
            'action_status': 'success',
            'msg': 'Изменения успешно внесены'
        }
        return JsonResponse(response_data)

    def form_invalid(self, form):
        response_data = {
            'action_status': 'danger',
            'msg': 'Что-то пошло не так, повторите попытку',
            'form_error': form.errors
        }
        return JsonResponse(response_data, status=400)


@available_for_learning
def lesson(request, dictionary_pk, user_pk):
    """
    The view create and render a new lesson:
    - crates required cards for new lesson;
    -  added to context obj lesson, cards;
    - added to context form to change number of answers;
    - added to context form to change status of card
    """
    dictionary = Dictionary.objects.\
        select_related('author'). \
        get(pk=dictionary_pk)

    current_lesson, created = Lesson.objects.get_or_create(
        dictionary=dictionary,
        student=request.user,
    )

    if created:
        current_lesson.create_cards()

    current_lesson.cards = Card.objects.filter(lesson=current_lesson).\
        select_related('word', 'lesson')

    for card in current_lesson.cards:
        card.form_card = ChangeCardStatus(
            initial={
                'status': card.status,
                'card_pk': card.pk,
                'back_url': request.path
            }
        )
    dictionary_form = ChoiceDictionaryForm(
        initial={
            'dictionary_pk': dictionary,
        }
    )
    form_answers = ChangeNumberAnswersForm(
        initial={
            'required_answers': current_lesson.required_answers,
            'lesson_pk': current_lesson.pk,
        }
    )

    context = dict(
        dictionary=dictionary,
        lesson=current_lesson,
        form_answers=form_answers,
        dictionary_form=dictionary_form,
    )

    return render(request, 'lesson.html', context=context)

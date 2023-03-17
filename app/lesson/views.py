from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect

from django.views.decorators.http import require_POST
from django.views.generic import FormView

from dictionary.decorators import available_for_learning
from dictionary.forms import ChoiceDictionaryForm

from lesson.forms import (
    ChangeNumberAnswersForm,
    ChangeCardStatus,
    LearnForm,
)
from lesson.models import Lesson, Card
from dictionary.models import Dictionary


@available_for_learning
def learn(request, reverse, lesson_pk):
    """
    View renders and checks answers.
    - reverse - is flag to direction of translation
    GET requests:
    - checks visited dict in session;
    - call lesson.get_random() to retrieve random and next cards;
    - no next_card means end of lesson;
    - add to context card and next_card and render;
    POST requests:
    - retrieve from form answer;
    - call card.check_card() to check answer and change card data;
    - append checked card to visited;
    - call current_lesson.get_next() to retrieve next_card;
    - no next_card triggers flushing visited;
    - add to context card and next_card and render;
    """
    visited = request.session.setdefault('visited', [])
    if request.method == 'POST':
        card = get_object_or_404(
            Card.objects.select_related(
                'lesson',
                'word',
                'lesson__dictionary'
            ),
            pk=request.POST.get('card_pk')
        )
        current_lesson = card.lesson
        next_card = current_lesson.get_next(card, visited)
        if not next_card:
            request.session['visited'] = []
        form = LearnForm(request.POST)
        if form.is_valid():
            visited.append(card.pk)
            cd = form.cleaned_data
            answer = cd['translations'].lower() or cd['body'].lower()
            status, msg = card.check_card(answer, reverse)

        else:
            status, msg = 'error', 'Что-то пошло не так, повторите попытку'

        if status == 'success':
            messages.success(request, msg)
        else:
            messages.error(request, msg)

    else:
        current_lesson = get_object_or_404(
            Lesson.objects.select_related('dictionary'),
            pk=lesson_pk
        )

        card, next_card = current_lesson.get_random(visited)

        if not card:
            if not current_lesson.get_active_cards():
                messages.error(
                    request,
                    'В выбранном словаре нет активных, '
                    'измените настройки словаря и попробуйте снова.'
                )
            request.session['visited'] = []
            request.session.modified = True
            return redirect(
                'lesson:lesson',
                dictionary_pk=current_lesson.dictionary.pk,
                user_pk=request.user.pk
            )

        form = LearnForm(
            initial={
                'card_pk': card.pk,
            },
        )
        if reverse:
            field = form.fields['translations']
        else:
            field = form.fields['body']

        field.widget = field.hidden_widget()

    request.session.modified = True
    context = {
        'card': card,
        'lesson': current_lesson,
        'form': form,
        'reverse': reverse,
        'next_card': next_card
    }
    return render(request, 'learn.html', context=context)


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

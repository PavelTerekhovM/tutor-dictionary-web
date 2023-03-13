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
    LearnFormReverse
)
from lesson.models import Lesson, Card
from dictionary.models import Dictionary


@available_for_learning
def learn(request, dictionary_pk, user_pk, card_pk, translation_reverse=False):
    """
    The view handles rendering and checking cards.
    translation_reverse - is flag to direction of
    translation
    When requested from lesson template the
    lesson.get_random takes first random card from
    lesson and pass it to this view.
    Template shows only question, example and field
    of form for answer.
    When answer sent, the view check if form valid and
    - increment number of attempt, correct answers,
    change status if achieved number of required
    answers and save data;
    - cards learned within lesson save in session and
    pass to lesson.get_random;
    - by function lesson.get_random takes random next card;
    - template shows correct answer and button to go
    to next card;
    """
    dictionary = Dictionary.objects.get(pk=dictionary_pk)
    lesson = get_object_or_404(Lesson, dictionary=dictionary, student=user_pk)
    cards = Card.objects.filter(lesson=lesson).\
        select_related('word').\
        select_related('lesson')
    card = Card.objects.get(pk=card_pk)
    if request.method == 'POST':
        # with translation_reverse flag function determines which form render
        if not translation_reverse:
            form = LearnForm(request.POST)
        else:
            form = LearnFormReverse(request.POST)
        card.all_attempts += 1
        if 'visited' in request.session:
            request.session['visited'].append(card_pk)
        else:
            request.session['visited'] = [card_pk]
        request.session.modified = True
        # word in form compare with data in db
        # split all word in answer and question and remove commas, ect
        # correct if answer in question
        if form.is_valid():
            cd = form.cleaned_data
            if not translation_reverse:
                answer = cd['translations'].lower()
                question = card.word.translations.lower()
            else:
                answer = cd['body'].lower()
                question = card.word.body.lower()
            chars = (",", ";", "...", "|", "\n", "\t", "n‘", "n’",
                          'n"', "n'", "‘", "’", '"', '  ', '   ', "'")
            for char in chars:
                answer = answer.replace(char, " ")
                question = question.replace(char, " ")
            if answer in question:
                card.correct_answers += 1
                card.all_correct_answers += 1
                # if required number of answers achieved change status
                if card.correct_answers == card.lesson.required_answers:
                    card.status = 'done'
                    messages.success(request, 'Карточка выучена')
                messages.success(request, 'Это верный ответ')
            else:
                messages.error(request, 'Это неверный ответ')
        card.save()
        # call function to get next random card
        next_card = lesson.get_random(
            card=card,
            visited=request.session['visited']
        )
        # if all card visited end learning, clear
        # visited and redirect to lesson
        if not next_card:
            request.session['visited'] = []
            request.session.modified = True
            return redirect(
                'lesson:lesson',
                dictionary_pk=dictionary_pk,
                user_pk=user_pk
            )
        # if next card exists add it to context
        # to enable show nextcard button in template
        context = {
            'dictionary': dictionary,
            'card': card,
            'next_card': next_card,
            'cards': cards,
            'lesson': lesson,
            'form': form,
            'translation_reverse': translation_reverse
        }
    else:
        if not translation_reverse:
            form = LearnForm()
        else:
            form = LearnFormReverse()
        context = {
            'dictionary': dictionary,
            'card': card,
            'cards': cards,
            'lesson': lesson,
            'form': form,
            'translation_reverse': translation_reverse
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

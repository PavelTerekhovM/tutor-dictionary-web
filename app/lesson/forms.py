from django import forms
from lesson.models import Lesson, Card

QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 11)]
STATUS_CHOICES = (
    ('', 'Изменить'),
    ('active', 'Учить'),
    ('done', 'Выучено'),
    ('disable', 'Отложено')
)


class LearnForm(forms.Form):
    card_pk = forms.ModelChoiceField(
        queryset=Card.objects.all(),
        widget=forms.HiddenInput,
    )
    translations = forms.CharField(
        max_length=300,
        required=False,
        label='',
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2})
    )
    body = forms.CharField(
        max_length=300,
        required=False,
        label='',
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2})
    )


class ChangeNumberAnswersForm(forms.Form):
    """
    Class describes a form to change numbers of required answers
    lesson_pk field - hidden input to identify lesson in view which
    handeling post request
    """
    required_answers = forms.TypedChoiceField(
        choices=QUANTITY_CHOICES,
        coerce=int,
        label='',
        widget=forms.Select()
    )
    lesson_pk = forms.ModelChoiceField(
        queryset=Lesson.objects.all(),
        widget=forms.HiddenInput,
    )


class ChangeCardStatus(forms.Form):
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        label='',
        # widget to submit by choosing option
        widget=forms.Select(
            attrs={'onchange': 'submit();'},
        )
    )
    card_pk = forms.ModelChoiceField(
        queryset=Card.objects.all(),
        widget=forms.HiddenInput,
    )
    back_url = forms.CharField(
        widget=forms.HiddenInput
    )

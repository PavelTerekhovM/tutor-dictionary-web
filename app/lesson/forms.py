from django import forms
from dictionary.models import Word

QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 11)]
STATUS_CHOICES = (
    ('', 'Изменить'),
    ('active', 'Учить'),
    ('done', 'Выучено'),
    ('disable', 'Отложено')
)


class LearnForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ('translations',)
        labels = {
            'translations': '',
        }
        widgets = {
            'translations': forms.Textarea(
                attrs={"class": "form-control", "rows": 2}
            )
        }


class LearnFormReverse(forms.ModelForm):
    """
    the form below required for reverse translation
    """
    class Meta:
        model = Word
        fields = ('body',)
        labels = {
            'body': '',
        }
        widgets = {
            'body': forms.Textarea(attrs={"class": "form-control", "rows": 2})
        }


class ChangeNumberAnswers(forms.Form):
    required_answers = forms.TypedChoiceField(
        required=False,
        choices=QUANTITY_CHOICES,
        coerce=int, label='',
        # widget to submit by choosing option
        widget=forms.Select(attrs={'onchange': 'submit();'})
    )


class ChangeCardStatus(forms.Form):
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        label='',
        # widget to submit by choosing option
        widget=forms.Select(attrs={'onchange': 'submit();'}))

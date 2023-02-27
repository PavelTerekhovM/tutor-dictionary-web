from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm
)
from .models import Dictionary
from django.contrib.auth.models import User


class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('old_password', 'new_password1', 'new_password2'):
            self.fields[field].widget.attrs = {'class': 'form-control'}
        self.fields['old_password'].label = 'Введите старый пароль'
        self.fields['new_password1'].label = 'Введите новый пароль'
        self.fields['new_password2'].label = 'Введите новый пароль повторно'


class AddStudentForm(forms.Form):
    update = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean(self):
        """
        additional validation by unique e-mail
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Пользователь с такой почтой уже зарегистрирован"
            )
        return self.cleaned_data


class DictionaryForm(forms.ModelForm):
    """
    form for uploading a new xml-dictionary
    """
    class Meta:
        model = Dictionary
        fields = ['note', 'status', 'file']
        labels = {
            'note': 'Примечания',
            'file': '',
            'status': '',
        }
        widgets = {
            'note': forms.Textarea(attrs={"class": "form-control", "rows": 5})
        }


class SearchForm(forms.Form):
    query = forms.CharField(label='')

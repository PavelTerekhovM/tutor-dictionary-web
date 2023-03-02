from xml.etree.ElementTree import ParseError
import xml.etree.ElementTree as ET

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm
)
from django.core.exceptions import ValidationError

from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import slugify

from .models import Dictionary, Word
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
    Form for uploading a new xml-dictionary
    """
    file = forms.FileField(
        validators=[FileExtensionValidator(
            allowed_extensions=['xml', 'csv', ],
        )],
        error_messages={
            'invalid_extension': 'Допустимые расширения словарей "xml" и "csv"'
        },
    )

    def __init__(self, *args, **kwargs):
        """
        Retrieving author from kwargs
        """
        self.author = kwargs['initial']['author']
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Creating dicrtionary instance and words instance
        while saving form while
        To do so:
        parse uploaded file
        - take parts of file in for-cycle  and add them
        in byte-string
        - find title of dictionary-file, create a new
        instance of dictionary
        - parse byte-string and find all cards, take words,
        translations and examples
        - create new instance of words for each card
        - assign all new word instances to the created dictionary
        """

        obj = super().save(False)
        obj.author = self.author
        uploaded_file = self.cleaned_data.get('file')
        # can't read uploaded_file, so add all lines to byte-string
        file = b''
        for line in uploaded_file:
            file += line

        # parse file with ElementTree module
        tree = ET.ElementTree(ET.fromstring(file))
        root = tree.getroot()
        obj.title = root.attrib['title']  # find name of file
        obj.slug = slugify(obj.title)
        # otherwise can't add many-to-many objects
        obj.save()

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
                    slug = slugify(body)
            for example in card.iter('example'):
                example = example.text      # find example of word

            # create and save new word in DB
            new_word = Word.objects.create(
                body=body,
                slug=slug,
                translations=translations,
                example=example)
            new_word.save()
            obj.word.add(new_word)
        obj.save()
        return obj

    def clean_file(self):
        """
        method to avoid files which can't be parsed afterwards
        due to unknown structure
        """
        uploaded_file = self.cleaned_data.get('file')
        if uploaded_file:
            try:
                file = b''
                for line in uploaded_file:
                    file += line
                tree = ET.ElementTree(ET.fromstring(file))
                root = tree.getroot()
                cards = []
                for card in root.iter('card'):
                    cards += card
                if not (root.attrib['title'] and cards):
                    raise ValidationError("Загруженный файл не был распознан")
                else:
                    return uploaded_file
            except ParseError:
                raise ValidationError("Загруженный файл не был распознан")
        raise ValidationError("Загруженный файл не был распознан")


    class Meta:
        model = Dictionary
        fields = ['author', 'note', 'status', 'file']
        labels = {
            'note': 'Примечания',
            'file': '',
            'status': '',
        }
        widgets = {
            'author': forms.HiddenInput(),
            'note': forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }
        required = ('status', 'file')


class SearchForm(forms.Form):
    query = forms.CharField(label='')

from django import forms

from django.core.exceptions import ValidationError

from django.core.validators import FileExtensionValidator

from .helpers import DictionaryFileManager
from .models import Dictionary


class AddStudentForm(forms.Form):
    dictionary_pk = forms.ModelChoiceField(
        queryset=Dictionary.objects.all(),
        required=True,
        widget=forms.HiddenInput,
    )


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

    def clean_file(self):
        """
        Method to avoid files which can't be parsed afterwards
        due to unknown structure
        """
        uploaded_file = self.cleaned_data.get('file')
        if DictionaryFileManager(uploaded_file).clean_file():
            return uploaded_file
        raise ValidationError("Загруженный файл не был распознан")

    def save(self, commit=True):
        """
        Creating dicrtionary instance and words instance
        while saving form while delegated to custom handler
        DictionaryFileManager
        """

        obj = super().save(False)
        obj.author = self.author
        uploaded_file = self.cleaned_data.get('file')
        obj = DictionaryFileManager(uploaded_file).parse_file(obj)
        return obj

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
        required = ('file', )


class SearchForm(forms.Form):
    query = forms.CharField(label='')

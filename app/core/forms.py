from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError


class UserRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in (
                'username', 'first_name', 'last_name',
                'email', 'password1', 'password2'
        ):
            self.fields[field].widget.attrs = {'class': 'form-control'}

        self.fields['username'].label = 'Имя пользователя'
        self.fields['username'].help_text = (
            'Обязательное поле, не менее 150 символов, '
            'только буквы, цифры и символы @/./+/-/_.'
        )
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].label = 'Почта'
        self.fields['password1'].label = 'Пароль'
        self.fields['password1'].help_text = (
            '<ul>'
            '<li>Пароль не должен быть похож на на предыдущие</li>'
            '<li>Пароль должен содержать не менее 8 символов.</li>'
            '<li>Пароль не может быть широко используемым.</li>'
            '<li>Пароль не может быть полностью числовым.</li>'
            '</ul>'
        )
        self.fields['password2'].label = 'Подтверждение пароля'
        self.fields['password2'].help_text = None

    class Meta:
        model = get_user_model()
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'password1', 'password2'
        )

    def clean(self):
        """
        additional validation by unique e-mail
        """
        email = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError(
                "Пользователь с такой почтой уже зарегистрирован"
            )
        return self.cleaned_data


class MyAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('username', 'password'):
            self.fields[field].widget.attrs = {'class': 'form-control'}
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password'].label = 'Пароль'



class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('old_password', 'new_password1', 'new_password2'):
            self.fields[field].widget.attrs = {'class': 'form-control'}
        self.fields['old_password'].label = 'Введите старый пароль'
        self.fields['new_password1'].label = 'Введите новый пароль'
        self.fields['new_password1'].help_text = (
            '<ul>'
            '<li>Пароль не должен быть похож на на предыдущие</li>'
            '<li>Пароль должен содержать не менее 8 символов.</li>'
            '<li>Пароль не может быть широко используемым.</li>'
            '<li>Пароль не может быть полностью числовым.</li>'
            '</ul>'
        )
        self.fields['new_password2'].label = 'Введите новый пароль повторно'

from django.contrib.auth.views import PasswordChangeView, LoginView
from django.urls import path, include


from core.views import SignUpView
from core.forms import MyPasswordChangeForm, MyAuthenticationForm


urlpatterns = [
    path('register/', SignUpView.as_view(), name='register'),
    path('login/', LoginView.as_view(form_class=MyAuthenticationForm), name='login'),
    path(
        'password_change/',
        PasswordChangeView.as_view(form_class=MyPasswordChangeForm),
        name='password_change'
    ),
    path('', include('django.contrib.auth.urls')),
]

from django.contrib.auth.views import PasswordChangeView
from django.urls import path, include


from core.views import SignUpView
from core.forms import MyPasswordChangeForm


urlpatterns = [
    path('register/', SignUpView.as_view(), name='register'),
    path(
        'password_change/',
        PasswordChangeView.as_view(form_class=MyPasswordChangeForm),
        name='password_change'
    ),
    path('', include('django.contrib.auth.urls')),
]

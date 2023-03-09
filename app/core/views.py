from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from core.forms import UserRegistrationForm


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')
    form_class = UserRegistrationForm
    success_message = "Вы успешно зарегистрировались на сайте Lingvo tutor"


def about(request):
    return render(request, 'about.html',)

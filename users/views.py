import secrets

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from .forms import CustomUserCreationForm, UserPasswordChangeForm
from .models import User

from config.settings import EMAIL_HOST_USER


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'customeruser_form.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/email-confirm/{token}'
        send_mail(subject="Подтверждение почты",
                  message=f"Привет, перейди по ссылке для подтверждения почты {url}",
                  from_email=EMAIL_HOST_USER,
                  recipient_list=[user.email])
        return super().form_valid(form)


class RegisterUpdateView(UpdateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'update_profile.html'
    success_url = reverse_lazy('users:login')
    def get_object(self, queryset=None):
        return self.request.user


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "password_change_form.html"
    extra_context = {'title': "Изменение пароля"}

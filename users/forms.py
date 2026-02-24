from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

from users.models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", )


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Автоматически добавляем класс 'form-input' ко всем полям формы
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-input'})

        # Опционально: уточняем русские названия, если они не подтянулись
        self.fields['old_password'].label = "Старый пароль"
        self.fields['new_password1'].label = "Новый пароль"
        self.fields['new_password2'].label = "Подтверждение пароля"
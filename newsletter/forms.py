from django import forms

from users.models import User
from .models import Newsletter, Message


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['start_time', 'end_time', 'message', 'recipients',]
        widgets = {
            'recipients': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '10'  # Показывать несколько строк
            }),
        }

    def __init__(self, *args, **kwargs):
        super(NewsletterForm, self).__init__(*args, **kwargs)

        self.fields['start_time'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'введите время начала рассылки'
        })

        self.fields['end_time'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'введите конец рассылки'
        })

        self.fields['message'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'введите сообщение'
        })


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['name_message', 'description_message', ]

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)

        self.fields['name_message'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'введите тему сообщения'
        })

        self.fields['description_message'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'введите содержание сообщения'
        })

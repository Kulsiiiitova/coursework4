from django.utils import timezone

from django.core.exceptions import ValidationError
from django.db import models

from users.models import User


class Message(models.Model):
    name_message = models.CharField(verbose_name="subject of the letter")
    description_message = models.CharField(verbose_name="body of the letter")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="owned_message", null=True, blank=True)

    def __str__(self):
        return self.name_message

    class Meta:
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        ordering = ['name_message', ]
        permissions = [
            ('view_all_messages', 'Может просматривать все сообщения'),
            ('can_disable_message', 'Может отключать сообщения'),
        ]


class Newsletter(models.Model):
    start_time = models.DateTimeField(verbose_name='mailing start time')
    end_time = models.DateTimeField(verbose_name='mailing end time')
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('launched', 'Launched'),
        ('completed', 'Completed')
    ]
    status = models.CharField(default='created', choices=STATUS_CHOICES, verbose_name='mailing status')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='message')
    recipients = models.ManyToManyField(User, verbose_name='пользователи', related_name='newsletters')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="owned_newsletter", null=True, blank=True)

    def clean(self):
        """Выполняет валидацию для времени"""
        if self.start_time and self.start_time < timezone.now():
            raise ValidationError("Время начала рассылки не может быть в прошлом.")

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Время начала рассылки должно быть раньше времени окончания.")

    def update_status(self):
        """
        Метод для обновления статуса на основе текущего времени.
        """
        now = timezone.now()
        if now < self.start_time:
            self.status = 'created'
        elif self.start_time <= now <= self.end_time:
            self.status = 'launched'
        elif now > self.end_time:
            self.status = 'completed'

    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'newsletter'

    class Meta:
        verbose_name = 'newsletter'
        verbose_name_plural = 'newsletters'
        ordering = ['message', ]
        permissions = [
            ('view_all_newsletters', 'Может просматривать все рассылки'),
            ('disable_newsletter', 'Может отключать рассылки'),
            ('can_change_newsletter_status', 'Может менять статус рассылок'),
        ]


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, verbose_name='newsletter', related_name='attempts')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='recipient', related_name='mailing_attempts', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='status')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='attempt time')
    server_response = models.TextField(verbose_name='ответ почтового сервера', blank=True, null=True)
    is_manual = models.BooleanField(default=False, verbose_name='ручная отправка')

    def __str__(self):
        return f"Attempt {self.id} - {self.status}"

    class Meta:
        verbose_name = 'mailing attempt'
        verbose_name_plural = 'mailing attempts'
        ordering = ['-created_at']

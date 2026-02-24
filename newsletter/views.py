import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib import messages

from config import settings
from newsletter.forms import NewsletterForm, MessageForm
from newsletter.models import Newsletter, Message, MailingAttempt
from users.models import User

import logging

logger = logging.getLogger(__name__)


@require_POST
@login_required
def send_newsletter_view(request, pk):
    """Отдельный view для отправки рассылки"""
    newsletter = get_object_or_404(Newsletter, pk=pk)

    # Детальная отладка времени
    now = timezone.now()
    logger.info("=" * 60)
    logger.info("ОТЛАДКА РАССЫЛКИ #%s", pk)
    logger.info("Текущее время: %s", now)
    logger.info("Начало рассылки: %s", newsletter.start_time)
    logger.info("Конец рассылки: %s", newsletter.end_time)
    logger.info("start_time <= now: %s", newsletter.start_time <= now)
    logger.info("now <= end_time: %s", now <= newsletter.end_time)
    logger.info("Можно отправлять: %s", newsletter.start_time <= now <= newsletter.end_time)
    logger.info("=" * 60)

    # Проверяем время рассылки
    if not (newsletter.start_time <= now <= newsletter.end_time):
        error_msg = (
            f"Нельзя отправить рассылку. "
            f"Текущее время: {now.strftime('%Y-%m-%d %H:%M:%S')}. "
            f"Время рассылки: {newsletter.start_time.strftime('%Y-%m-%d %H:%M:%S')} - "
            f"{newsletter.end_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        logger.error(error_msg)
        messages.error(request, error_msg)

        # Создаем запись о неудачной попытке
        MailingAttempt.objects.create(
            newsletter=newsletter,
            status='failed',
            server_response=error_msg,
            is_manual=True
        )
        return redirect('newsletter:newsletter_details', pk=pk)

    # Проверяем получателей
    recipients = newsletter.recipients.all()
    logger.info("Количество получателей: %s", recipients.count())

    if not recipients.exists():
        error_msg = "Нет получателей для отправки рассылки"
        logger.warning(error_msg)
        messages.warning(request, error_msg)

        MailingAttempt.objects.create(
            newsletter=newsletter,
            status='failed',
            server_response=error_msg,
            is_manual=True
        )
        return redirect('newsletter:newsletter_details', pk=pk)

    success_count = 0
    failed_count = 0

    for recipient in recipients:
        logger.info("Обработка получателя: %s (email: %s)", recipient.username, recipient.email)

        try:
            # Проверяем наличие email
            if not recipient.email:
                raise ValueError(f"У пользователя {recipient.username} нет email")

            # Отправляем письмо
            subject = newsletter.message.name_message if newsletter.message else "Рассылка"
            message_text = f"""
            Здравствуйте, {recipient.first_name or recipient.username}!

            {newsletter.message.description_message if newsletter.message else ''}

            ---
            Рассылка #{newsletter.id}
            Отправлено: {now.strftime('%d.%m.%Y %H:%M')}
            """

            logger.info("Отправка письма на %s", recipient.email)

            send_mail(
                subject=subject,
                message=message_text,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient.email],
                fail_silently=False
            )
            # Создаем запись об успешной попытке
            MailingAttempt.objects.create(
                newsletter=newsletter,
                recipient=recipient,
                status='success',
                server_response='Письмо успешно отправлено',
                is_manual=True
            )

            success_count += 1
            logger.info("УСПЕХ: письмо отправлено на %s", recipient.email)

        except Exception as e:
            error_msg = str(e)
            logger.error("ОШИБКА для %s: %s", recipient.email, error_msg)

            # Создаем запись о неудачной попытке
            MailingAttempt.objects.create(
                newsletter=newsletter,
                recipient=recipient,
                status='failed',
                server_response=f'Ошибка: {error_msg}',
                is_manual=True
            )

            failed_count += 1

        # Итоговая статистика
        logger.info("ИТОГО: Успешно %s, Неудачно %s", success_count, failed_count)

        # Сообщения о результатах
        if success_count > 0:
            success_msg = f"Рассылка успешно отправлена {success_count} пользователям!"
            messages.success(request, success_msg)
            logger.info(success_msg)

        if failed_count > 0:
            warning_msg = f"Не удалось отправить {failed_count} пользователям"
            messages.warning(request, warning_msg)
            logger.warning(warning_msg)

        return redirect('newsletter:newsletter_details', pk=pk)


class NewsletterListView(ListView):
    model = Newsletter
    template_name = 'newsletter/newsletter-list.html'
    context_object_name = 'newsletters'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        object_count_total = Newsletter.objects.count()
        object_count_launched = Newsletter.objects.filter(status='launched').count()
        count_users = User.objects.count()
        context['newsletter_count'] = object_count_total
        context['newsletter_count_launched'] = object_count_launched
        context['count_users'] = count_users
        context['messages'] = Message.objects.all()

        return context


@method_decorator(cache_page(60 * 15), name='dispatch')
class NewsletterDetailView(DetailView):
    model = Newsletter
    template_name = 'newsletter/newsletter-details.html'
    context_object_name = 'newsletter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_attempts'] = self.object.attempts.all()[:10]  # последние 10 попыток
        context['success_count'] = self.object.attempts.filter(status='success').count()
        context['failed_count'] = self.object.attempts.filter(status='failed').count()
        return context


class NewsletterCreateView(CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'newsletter/newsletter-form.html'
    success_url = reverse_lazy('newsletter:newsletter_list')




class NewsletterDeleteView(DeleteView):
    model = Newsletter
    template_name = 'newsletter/newsletter-confirm-delete.html'
    success_url = reverse_lazy('newsletter:newsletter_list')
    context_object_name = 'newsletter'
    permission_required = 'newsletter.can_delete_product'


class NewsletterUpdateView(UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'newsletter/newsletter-form.html'
    success_url = reverse_lazy('newsletter:newsletter_list')


# class MessageListView(ListView):
#     model = Message
#     template_name = 'newsletter/newsletter-list.html'
#     context_object_name = 'messages'


class MessageDetailView(DetailView):
    model = Message
    template_name = 'message/message-details.html'
    context_object_name = 'message'


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'message/message-form.html'
    success_url = reverse_lazy('newsletter:newsletter_list')

# def form_valid(self, form):
    #     response = super().form_valid(form)
    #     all_users = User.objects.all()
    #     self.object.recipients.set(all_users)
    #     return response
        # form.instance.recipients = self.request.user
        # return super().form_valid(form)


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'message/message-confirm-delete.html'
    success_url = reverse_lazy('newsletter:newsletter_list')
    context_object_name = 'message'
    permission_required = 'newsletter.can_delete_product'


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'message/message-form.html'
    success_url = reverse_lazy('newsletter:newsletter_list')
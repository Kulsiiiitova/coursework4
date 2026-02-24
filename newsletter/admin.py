from django.contrib import admin
from .models import Newsletter, Message, MailingAttempt


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_message_name', 'start_time', 'end_time', 'status', 'get_recipients_count')
    list_filter = ('status', 'start_time')
    filter_horizontal = ('recipients',)
    search_fields = ('message__name_message',)

    def get_message_name(self, obj):
        return obj.message.name_message

    get_message_name.short_description = 'Сообщение'

    def get_recipients_count(self, obj):
        return obj.recipients.count()

    get_recipients_count.short_description = 'Получателей'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_message', 'get_description_preview')
    search_fields = ('name_message', 'description_message')

    def get_description_preview(self, obj):
        return obj.description_message[:100] + '...' if len(obj.description_message) > 100 else obj.description_message

    get_description_preview.short_description = 'Описание'


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_newsletter_id', 'get_recipient_email', 'status', 'created_at', 'is_manual')
    list_filter = ('status', 'is_manual', 'created_at')
    search_fields = ('newsletter__id', 'recipient__email', 'server_response')
    readonly_fields = ('created_at',)

    def get_newsletter_id(self, obj):
        return f"#{obj.newsletter.id}"

    get_newsletter_id.short_description = 'Рассылка'

    def get_recipient_email(self, obj):
        return obj.recipient.email if obj.recipient else 'Не указан'

    get_recipient_email.short_description = 'Получатель'
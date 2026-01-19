from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Создание групп пользователей'

    def handle(self, *args, **kwargs):
        # Создаем группы
        Group.objects.get_or_create(name='Пользователь')
        Group.objects.get_or_create(name='Менеджер')

        self.stdout.write(self.style.SUCCESS('✅ Группы созданы: Пользователь, Менеджер'))
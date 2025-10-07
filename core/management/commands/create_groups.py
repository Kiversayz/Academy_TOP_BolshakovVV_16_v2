from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Создаёт группы пользователей: Moderator, Admin'

    def handle(self, *args, **options):
        # Создаём группы
        moderator_group, created = Group.objects.get_or_create(name='Moderator')
        admin_group, created = Group.objects.get_or_create(name='Admin')

        if created:
            self.stdout.write(f"Группа '{moderator_group.name}' создана.")
            self.stdout.write(f"Группа '{admin_group.name}' создана.")
        else:
            self.stdout.write("Группы уже существуют.")
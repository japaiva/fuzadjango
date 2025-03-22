# management/commands/init_db.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from .utils import hash_password

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize database and create admin user'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'fuza1234', nivel='admin')
            self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin user already exists'))
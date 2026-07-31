from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create the default admin superuser if it does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Admin user already exists, skipping.'))
            return
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.stdout.write(self.style.SUCCESS('Admin user created (admin/admin123).'))

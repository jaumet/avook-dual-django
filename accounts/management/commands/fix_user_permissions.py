from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Fixes the permissions of existing users who are staff but not superusers.'

    def handle(self, *args, **options):
        User = get_user_model()
        users_to_fix = User.objects.filter(is_staff=True, is_superuser=False)

        if not users_to_fix.exists():
            self.stdout.write(self.style.SUCCESS('No users needed fixing.'))
            return

        self.stdout.write(f'Found {users_to_fix.count()} users to fix.')

        for user in users_to_fix:
            user.is_staff = False
            user.save()
            self.stdout.write(f'Fixed user: {user.username}')

        self.stdout.write(self.style.SUCCESS('Successfully fixed user permissions.'))

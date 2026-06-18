"""
Creates a default admin account on first run, so the clinic has a way in
before anyone has manually run createsuperuser.

Usage:
    python manage.py seed_admin
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates a default admin account (admin / admin123) if one does not already exist."

    def handle(self, *args, **options):
        if User.objects.filter(username="admin").exists():
            self.stdout.write(self.style.WARNING("'admin' account already exists — nothing to do."))
            return

        user = User.objects.create_user(
            username="admin",
            password="admin123",
            first_name="Administrator",
            is_staff=True,
            is_superuser=True,
        )
        # No need to create StaffProfile manually — the post_save signal in
        # records/signals.py already creates one automatically (role="admin"
        # because is_superuser=True).
        self.stdout.write(self.style.SUCCESS(
            "Default admin account created — username: admin / password: admin123\n"
            "IMPORTANT: change this password after your first login."
        ))

"""
Auto-logging via Django's built-in auth signals.
This means login/logout/failed-login audit entries are created automatically
the moment Django's auth system fires these signals — no extra code needed
in the views themselves.
"""
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AuditLog, StaffProfile


@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    AuditLog.log(user, "LOGIN", f"User '{user.username}' logged in")


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user:
        AuditLog.log(user, "LOGOUT", f"User '{user.username}' logged out")


@receiver(user_login_failed)
def log_failed_login(sender, credentials, **kwargs):
    username = credentials.get("username", "unknown")
    AuditLog.log(None, "FAILED_LOGIN", f"Failed login attempt for '{username}'")


@receiver(post_save, sender=User)
def ensure_staff_profile(sender, instance, created, **kwargs):
    """
    Guarantees every User has a StaffProfile, even if the account was made
    with `python manage.py createsuperuser` instead of through the app's own
    "Add Dentist" form. Superusers default to the admin role; everyone else
    defaults to dentist.
    """
    if created and not StaffProfile.objects.filter(user=instance).exists():
        StaffProfile.objects.create(
            user=instance,
            role="admin" if instance.is_superuser else "dentist",
        )

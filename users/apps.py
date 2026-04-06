from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        from django.conf import settings as s
        from django.db.models.signals import post_migrate
        post_migrate.connect(_seed_admin, sender=self)


def _seed_admin(sender, **kwargs):
    from django.conf import settings as s
    from users.models import User, Role
    if not User.objects.filter(deleted_at__isnull=True).exists():
        User.objects.create_user(
            username=s.ADMIN_USERNAME,
            email=s.ADMIN_EMAIL,
            password=s.ADMIN_PASSWORD,
            first_name="Admin",
            last_name="User",
            role=Role.ADMIN,
        )

from django.apps import AppConfig


class ReplacedDjangoStaticConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'replaced_django_static'

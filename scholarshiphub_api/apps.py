from django.apps import AppConfig


class ScholarshiphubApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scholarshiphub_api'

    def ready(self):
        import scholarshiphub_api.signals

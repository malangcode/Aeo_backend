from django.apps import AppConfig


class aeoappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aeoApp'
    
    def ready(self):
        import aeoApp.signals




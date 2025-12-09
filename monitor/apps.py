from django.apps import AppConfig
import os

class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'

    def ready(self):
        # Evita rodar 2x por causa do autoreload
        if os.environ.get('RUN_MAIN') == 'true':
            from .mqtt_client import start_mqtt
            start_mqtt()

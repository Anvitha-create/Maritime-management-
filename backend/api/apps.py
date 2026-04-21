from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    scheduler_started = False

    def ready(self):
        if ApiConfig.scheduler_started:
            return

        ApiConfig.scheduler_started = True

        try:
            from . import scheduler  # Your scheduler.py with BackgroundScheduler
            scheduler.start()
        except Exception as e:
            print("⚠️ Scheduler start error:", e)
from django.core.management.base import BaseCommand
from api.ghost_detector import check_ais_timeout
import time

CHECK_INTERVAL = 10  # seconds

class Command(BaseCommand):
    help = "Continuously checks for ghost vessels"

    def handle(self, *args, **kwargs):
        print("🚀 Ghost vessel scheduler started")
        try:
            while True:
                check_ais_timeout()
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("🛑 Ghost vessel scheduler stopped")
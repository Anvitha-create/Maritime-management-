from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import apps
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import random

scheduler = BackgroundScheduler()

def update_vessels():
    """
    Periodically called function to update vessel positions.
    You can replace this with real AIS/API data.
    """
    Vessel = apps.get_model("api", "Vessel")  # Get Vessel model dynamically
    vessels = Vessel.objects.all()
    channel_layer = get_channel_layer()

    for vessel in vessels:
        # Example: Random small position update for demo purposes
        vessel.latitude += random.uniform(-0.01, 0.01)
        vessel.longitude += random.uniform(-0.01, 0.01)
        vessel.save(update_fields=["latitude", "longitude"])

        # Trigger live broadcast via Channels
        async_to_sync(channel_layer.group_send)(
            "vessel_updates",
            {
                "type": "send_vessel_update",
                "vessel": {
                    "id": vessel.id,
                    "name": vessel.name,
                    "lat": vessel.latitude,
                    "lng": vessel.longitude,
                    "vessel_type": vessel.vessel_type,
                    "status": vessel.status,
                    "current_port": vessel.current_port.name if vessel.current_port else None
                }
            }
        )

def start():
    # Add the job if it doesn't exist already
    if not scheduler.get_jobs():
        scheduler.add_job(update_vessels, "interval", seconds=10, id="update_vessels")
        scheduler.start()
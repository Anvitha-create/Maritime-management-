import redis
import time
from django.apps import apps
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Redis connection
r = redis.Redis(host="localhost", port=6379, db=0)

AIS_TIMEOUT = 120  # seconds, adjust as needed


# -----------------------------
# Update vessel AIS activity
# -----------------------------
def update_vessel(vessel_id, lat, lon):
    Vessel = apps.get_model("api", "Vessel")

    try:
        vessel = Vessel.objects.select_related("current_port").get(id=vessel_id)
    except Vessel.DoesNotExist:
        return

    now = int(time.time())

    # Store vessel info in a Redis hash
    r.hset(f"vessel:{vessel_id}", mapping={
        "last_seen": now,
        "lat": lat,
        "lon": lon
    })

    # Only broadcast if coordinates changed or vessel was Ghost
    coordinates_changed = vessel.latitude != lat or vessel.longitude != lon
    if coordinates_changed or vessel.status == "Ghost":
        if vessel.status == "Ghost":
            vessel.status = "Active"
        vessel.latitude = lat
        vessel.longitude = lon
        vessel.save()
        broadcast_vessel(vessel, lat, lon)


# -----------------------------
# Broadcast helper
# -----------------------------
def broadcast_vessel(vessel, lat, lon):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "vessel_updates",
        {
            "type": "send_vessel_update",
            "vessel": {
                "id": vessel.id,
                "name": vessel.name,
                "vessel_type": vessel.vessel_type,
                "current_port": vessel.current_port.name if vessel.current_port else None,
                "status": vessel.status,
                "latitude": lat,
                "longitude": lon,
            }
        }
    )
    print(f"📡 Broadcasted vessel {vessel.name}")


# -----------------------------
# Ghost detection
# -----------------------------
def check_ais_timeout():
    Vessel = apps.get_model("api", "Vessel")
    now = int(time.time())

    # Only scan keys that are hashes (ignore old string keys)
    for key in r.keys("vessel:*"):
        try:
            if r.type(key).decode() != "hash":
                continue

            data = r.hgetall(key)
            if not data:
                continue

            vessel_id = key.decode().split(":")[1]
            last_seen = int(data.get(b"last_seen", 0))
            lat = float(data.get(b"lat", 0))
            lon = float(data.get(b"lon", 0))

            try:
                vessel = Vessel.objects.get(id=vessel_id)
            except Vessel.DoesNotExist:
                continue

            # Only act if status changes
            if now - last_seen > AIS_TIMEOUT:
                if vessel.status != "Ghost":
                    vessel.status = "Ghost"
                    vessel.save()
                    broadcast_vessel(vessel, lat, lon)
                    print(f"🚨 {vessel.name} marked as Ghost")
            else:
                if vessel.status == "Ghost":
                    vessel.status = "Active"
                    vessel.save()
                    broadcast_vessel(vessel, lat, lon)
                    print(f"🟢 {vessel.name} restored to Active")

        except redis.exceptions.ResponseError:
            # Skip any key that is not a hash
            continue
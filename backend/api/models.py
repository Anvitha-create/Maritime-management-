from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta

# ====================== USER ======================
class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("analyst", "Analyst"),
        ("operator", "Operator"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="operator")
    receive_event_notifications = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

# ====================== PORT ======================
class Port(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.name}, {self.country}"

# ====================== VESSEL ======================
class Vessel(models.Model):
    VESSEL_TYPES = [
        ("Cargo", "Cargo"),
        ("Tanker", "Tanker"),
        ("Passenger", "Passenger"),
    ]

    name = models.CharField(max_length=100)
    vessel_type = models.CharField(max_length=50, choices=VESSEL_TYPES)
    capacity = models.PositiveIntegerField()
    current_port = models.ForeignKey(
        Port,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vessels",
    )
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, default="Active")

    def __str__(self):
        return self.name

# ====================== VOYAGE ======================
class Voyage(models.Model):
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name="voyages")
    origin = models.ForeignKey(Port, on_delete=models.CASCADE, related_name="departures")
    destination = models.ForeignKey(Port, on_delete=models.CASCADE, related_name="arrivals")
    departure_date = models.DateField()
    arrival_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.departure_date and not self.arrival_date:
            self.arrival_date = self.departure_date + timedelta(days=7)
        super().save(*args, **kwargs)

        # Create Departure event only if new
        if not self.pk:
            Event.objects.create(voyage=self, event_type="Departure", description="Voyage started.")

    def __str__(self):
        return f"{self.vessel.name} | {self.origin.name} → {self.destination.name}"

# ====================== EVENT ======================
class Event(models.Model):
    EVENT_TYPES = [
        ("Departure", "Departure"),
        ("Arrival", "Arrival"),
        ("Delay", "Delay"),
    ]
    voyage = models.ForeignKey(Voyage, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            users = User.objects.filter(receive_event_notifications=True)
            notifications = [
                Notification(user=user, message=f"{self.event_type} event for voyage {self.voyage}")
                for user in users
            ]
            Notification.objects.bulk_create(notifications)

    def __str__(self):
        return f"{self.event_type} - {self.voyage}"

# ====================== NOTIFICATION ======================
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
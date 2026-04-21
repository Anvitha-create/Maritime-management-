from django.contrib import admin
from .models import User, Port, Vessel, Voyage, Event, Notification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff")
    list_filter = ("role", "is_staff")
    search_fields = ("username", "email")


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name", "country")


@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    list_display = ("name", "vessel_type", "capacity", "current_port")
    list_filter = ("vessel_type",)
    search_fields = ("name",)


@admin.register(Voyage)
class VoyageAdmin(admin.ModelAdmin):
    list_display = (
        "vessel",
        "origin",
        "destination",
        "departure_date",
        "arrival_date",
    )
    list_filter = ("departure_date",)
    search_fields = ("vessel__name",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("voyage", "event_type", "timestamp")
    list_filter = ("event_type",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "is_read", "created_at")
    list_filter = ("is_read",)

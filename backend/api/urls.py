from django.urls import path, include
from rest_framework import routers
from .views import (
    PortViewSet,
    VesselViewSet,
    VoyageViewSet,
    EventViewSet,              # ✅ Added
    NotificationViewSet,       # ✅ Added
    CurrentUserView,
    UserRegistrationView,
    live_map,
)

# -------------------------
# DRF Router for viewsets
# -------------------------
router = routers.DefaultRouter()
router.register(r"ports", PortViewSet, basename="port")
router.register(r"vessels", VesselViewSet, basename="vessel")
router.register(r"voyages", VoyageViewSet, basename="voyage")
router.register(r"events", EventViewSet, basename="event")                # ✅ Added
router.register(r"notifications", NotificationViewSet, basename="notification")  # ✅ Added

# -------------------------
# URL Patterns
# -------------------------
urlpatterns = [

    # 🌍 Interactive Map Page
    path("map/", live_map, name="live-map"),

    # DRF Viewsets
    path("", include(router.urls)),

    # Current authenticated user
    path("me/", CurrentUserView.as_view(), name="current-user"),

    # User registration
    path("register/", UserRegistrationView.as_view(), name="register"),
]
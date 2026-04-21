# api/views.py
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import User, Port, Vessel, Voyage, Event, Notification
from .serializers import (
    PortSerializer, VesselSerializer, VoyageSerializer, UserSerializer,
    RegisterSerializer, EventSerializer, NotificationSerializer
)
import random


# ----------------- LIVE MAP -----------------
def live_map(request):
    return render(request, "map.html")


# ----------------- BROADCAST FUNCTION -----------------
def broadcast_vessel_update(vessel):
    """
    Sends live vessel data via Django Channels to front-end.
    """
    channel_layer = get_channel_layer()
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


# ----------------- ROLE PERMISSION -----------------
class RolePermission(BasePermission):
    """
    Custom role-based permission. Only allows access if user.role is in view.allowed_roles.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        allowed_roles = getattr(view, "allowed_roles", [])
        return request.user.role in allowed_roles


# ----------------- PORT VIEWSET -----------------
class PortViewSet(viewsets.ModelViewSet):
    queryset = Port.objects.all()
    serializer_class = PortSerializer
    allowed_roles = ["admin", "operator"]

    def get_permissions(self):
        return [RolePermission()]


# ----------------- VESSEL VIEWSET -----------------
class VesselViewSet(viewsets.ModelViewSet):
    queryset = Vessel.objects.all()
    serializer_class = VesselSerializer
    allowed_roles = ["admin"]

    def get_permissions(self):
        return [RolePermission()]

    def perform_update(self, serializer):
        vessel = serializer.save()
        broadcast_vessel_update(vessel)


# ----------------- VOYAGE VIEWSET -----------------
class VoyageViewSet(viewsets.ModelViewSet):
    queryset = Voyage.objects.all()
    serializer_class = VoyageSerializer

    # ⚡ TEMPORARY: Allow public access so front-end map can load dotted lines
    permission_classes = [AllowAny]

    # If you want JWT auth, replace with:
    # permission_classes = [IsAuthenticated]
    # allowed_roles = ["admin", "analyst"]
    # def get_permissions(self):
    #     return [RolePermission()]


# ----------------- EVENT VIEWSET -----------------
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]


# ----------------- NOTIFICATION VIEWSET -----------------
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]


# ----------------- CURRENT USER -----------------
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# ----------------- USER REGISTRATION -----------------
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Self-registration endpoint. Users cannot choose role here.
        Default role: 'analyst'. Only admin can update roles later.
        """
        data = request.data.copy()
        data["role"] = "analyst"  # Force default role
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User created successfully",
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------- SCHEDULER -----------------
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def update_vessels():
    """
    Periodically updates vessel positions randomly.
    """
    vessels = Vessel.objects.all()
    for vessel in vessels:
        vessel.latitude += random.uniform(-0.01, 0.01)
        vessel.longitude += random.uniform(-0.01, 0.01)
        vessel.save(update_fields=["latitude", "longitude"])
        broadcast_vessel_update(vessel)

def start_scheduler():
    if not scheduler.get_jobs():
        scheduler.add_job(update_vessels, "interval", seconds=10, id="update_vessels")
        scheduler.start()
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Port, Vessel, Voyage, Event, Notification


# =========================
# USER SERIALIZER (READ-ONLY)
# =========================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]
        read_only_fields = ["id", "username", "role"]


# =========================
# USER REGISTRATION SERIALIZER
# =========================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        default="operator",
        required=False,
    )

    class Meta:
        model = User
        fields = ["username", "password", "email", "role"]

    def create(self, validated_data):
        role = validated_data.get("role", "operator")

        # 🚨 SECURITY RULE
        # Users MUST NOT self-register as admin
        if role not in ["operator", "analyst"]:
            role = "operator"

        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email"),
            role=role,
        )
        return user


# =========================
# PORT SERIALIZER
# =========================
class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = "__all__"


# =========================
# VESSEL SERIALIZER
# =========================
class VesselSerializer(serializers.ModelSerializer):
    current_port_name = serializers.CharField(
        source="current_port.name",
        read_only=True,
        default=None
    )

    class Meta:
        model = Vessel
        fields = [
            "id",
            "name",
            "vessel_type",
            "capacity",
            "current_port",
            "current_port_name",
        ]


# =========================
# =========================
# VOYAGE SERIALIZER
# =========================
class VoyageSerializer(serializers.ModelSerializer):
    vessel_name = serializers.CharField(source="vessel.name", read_only=True)

    origin_name = serializers.CharField(source="origin.name", read_only=True)
    origin_lat = serializers.FloatField(source="origin.latitude", read_only=True)
    origin_lng = serializers.FloatField(source="origin.longitude", read_only=True)

    destination_name = serializers.CharField(source="destination.name", read_only=True)
    destination_lat = serializers.FloatField(source="destination.latitude", read_only=True)
    destination_lng = serializers.FloatField(source="destination.longitude", read_only=True)

    class Meta:
        model = Voyage
        fields = [
            "id",
            "vessel_name",

            "origin_name",
            "origin_lat",
            "origin_lng",

            "destination_name",
            "destination_lat",
            "destination_lng",

            "departure_date",
            "arrival_date",
        ]
# =========================
# EVENT SERIALIZER
# =========================
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["timestamp"]


# =========================
# NOTIFICATION SERIALIZER
# =========================
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ["created_at"]

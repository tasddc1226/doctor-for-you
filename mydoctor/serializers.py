from rest_framework import serializers
from .models import Doctor


class DoctorNameSerializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = Doctor
        fields = ["name"]

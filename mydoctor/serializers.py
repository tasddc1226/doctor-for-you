from rest_framework import serializers
from .models import Doctor, CareRequestList


class DoctorNameSerializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = Doctor
        fields = ["name"]


class CareRequestSerializer(serializers.Serializer):
    class Meta:
        model = CareRequestList
        fields = "__all__"

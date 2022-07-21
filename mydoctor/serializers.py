from rest_framework import serializers
from .models import Doctor, CareRequestList


class DoctorNameSerializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = Doctor
        fields = ["name"]


class CareRequestSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    def get_patient_name(self, obj):
        return obj.patient.name

    def get_doctor_name(self, obj):
        return obj.doctor.name

    class Meta:
        model = CareRequestList
        fields = "__all__"


class CareRequestListSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()

    def get_patient_name(self, obj):
        return obj.patient.name

    class Meta:
        model = CareRequestList
        fields = [
            "id",
            "patient_name",
            "book_time",
            "expire_time",
        ]

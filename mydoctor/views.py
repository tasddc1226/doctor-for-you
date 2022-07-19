from pydoc import doc
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from django.db.models import Q

from .models import Doctor, Patient, WeekDayTime, WeekendTime
from .serializers import DoctorNameSerializer


class DoctorSeaerchView(ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorNameSerializer

    def get(self, request, *args, **kwargs):
        dept_name = request.GET.get("dept", None)
        hospital_name = request.GET.get("hospital", None)
        doctor_name = request.GET.get("doctor", None)
        non_paid_dept_name = request.GET.get("non_paid", None)

        q = Q()

        if dept_name:
            q &= Q(dept__icontains=dept_name)

        if hospital_name:
            q &= Q(hospital__icontains=hospital_name)

        if doctor_name:
            q &= Q(name__icontains=doctor_name)

        if non_paid_dept_name:
            q &= Q(non_paid__icontains=non_paid_dept_name)

        objs = Doctor.objects.filter(q)

        serializer = self.get_serializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

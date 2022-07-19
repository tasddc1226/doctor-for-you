from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from django.db.models import Q

from .models import Doctor, Patient, WeekDayTime, WeekendTime
from .serializers import DoctorNameSerializer
import json
import datetime


class DoctorSeaerchView(ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorNameSerializer

    def get(self, request, *args, **kwargs):
        """
        input : 검색 조건 쿼리
        output : 검색 조건에 맞는 의사 리스트
        """
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

    def post(self, request, *args, **kwargs):
        """
        input : 특정 날짜와 시간
        output : 영업 중인 의사 리스트
        """
        data = json.loads(request.body)
        date = datetime.datetime(
            data["year"], data["month"], data["day"], data["hour"]
        )
        no = date.isoweekday()

        if no < 6:
            queryset = WeekDayTime.objects.select_related("doctor")

        else:
            queryset = WeekendTime.objects.select_related("doctor").filter(
                closed=False
            )

        objs = queryset.filter(
            to_hour__gte=data["hour"], from_hour__lte=data["hour"]
        ).values_list("doctor")

        results = self.get_queryset().filter(id__in=objs)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

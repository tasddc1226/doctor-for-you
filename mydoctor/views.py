from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Doctor, Patient, WeekDayTime, WeekendTime, CareRequestList
from .serializers import DoctorNameSerializer, CareRequestSerializer
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
            # 평일인 경우
            queryset = WeekDayTime.objects.select_related("doctor")

        else:
            # 주말인 경우
            queryset = WeekendTime.objects.select_related("doctor").filter(
                closed=False
            )

        objs = queryset.filter(
            Q(to_hour__gte=data["hour"], lunch_to__lt=data["hour"])
            | Q(lunch_from__gt=data["hour"], from_hour__lte=data["hour"])
        ).values_list("doctor")

        results = self.get_queryset().filter(id__in=objs)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CareRequestView(ListAPIView):
    queryset = CareRequestList.objects.all()
    serializer_class = CareRequestSerializer

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        print(data)
        ## 환자 id, 의사 id 예외 처리
        patient = get_object_or_404(Patient, id=data["patient_id"])
        doctor = get_object_or_404(Doctor, id=data["doctor_id"])

        ## 요청된 예약 진료 시각에 대하여 해당 의사가 진료 가능한지 확인
        date = datetime.datetime(
            data["year"], data["month"], data["day"], data["hour"]
        )
        no = date.isoweekday()
        print(date)

        if no < 6:
            # 진료 요청일이 평일인 경우
            queryset = WeekDayTime.objects.filter(doctor=data["doctor_id"])
        else:
            # 진료 요청일이 주말인 경우
            queryset = WeekendTime.objects.filter(
                doctor=data["doctor_id"], closed=False
            )

        objs = queryset.filter(
            Q(to_hour__gte=data["hour"], lunch_to__lt=data["hour"])
            | Q(lunch_from__gt=data["hour"], from_hour__lte=data["hour"])
        )

        if objs:
            # TODO: 예약이 가능하다면 요청 만료 시각 계산
            ## -> 진료 요청한 후 +20분까지 예약이 유효함.
            ## -> 만약 요청된 시간에 의사가 부재일 경우 다음날 Or 점심시간 이후 +15분 까지 유효
            pass
        else:
            return Response(
                {"message": "진료 예약이 불가능합니다. 다른 시간을 선택해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_200_OK)

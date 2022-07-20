from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from django.db.models import Q
from django.shortcuts import get_object_or_404

import json
from .models import Doctor, Patient, WeekDayTime, WeekendTime, CareRequestList
from .serializers import DoctorNameSerializer, CareRequestSerializer
from datetime import datetime, timedelta, date


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
        date_from_data = datetime(
            data["year"],
            data["month"],
            data["day"],
            data["hour"],
            data["min"],
        )
        no = date_from_data.isoweekday()

        if no < 6:
            # 평일인 경우
            queryset = WeekDayTime.objects.select_related("doctor")
            objs = queryset.filter(
                Q(to_hour__gte=data["hour"], lunch_to__lt=data["hour"])
                | Q(lunch_from__gt=data["hour"], from_hour__lte=data["hour"])
            ).values_list("doctor")

        else:
            # 주말인 경우
            queryset = WeekendTime.objects.select_related("doctor").filter(
                closed=False
            )
            objs = queryset.filter(
                to_hour__gte=data["hour"], from_hour__lte=data["hour"]
            ).values_list("doctor")

        results = self.get_queryset().filter(id__in=objs)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CareRequestView(ListAPIView):
    queryset = CareRequestList.objects.all()
    serializer_class = CareRequestSerializer

    def _is_valid_request_ids(self, p_id, d_id):
        ## 환자 id, 의사 id 예외 처리
        patient = get_object_or_404(Patient, id=p_id)
        doctor = get_object_or_404(Doctor, id=d_id)

    def _convert_hour_list_to_datetime_object_list(self, hour_list, now):
        res = []
        for hour in hour_list:
            res.append(
                datetime(now.year, now.month, now.day) + timedelta(hours=hour)
            )
        return res

    def _set_conditions(self, datetime_objs_list, now):
        if len(datetime_objs_list) > 2:
            is_workday_weekday = (
                datetime_objs_list[0] <= now < datetime_objs_list[1]
                or datetime_objs_list[2] <= now < datetime_objs_list[3]
            )
            is_lunch_time = datetime_objs_list[1] <= now < datetime_objs_list[2]
            is_workday_weekend = False
        else:
            is_workday_weekday = False
            is_workday_weekend = (
                datetime_objs_list[0] <= now < datetime_objs_list[1]
            )
            is_lunch_time = False
        return is_workday_weekday, is_workday_weekend, is_lunch_time

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        self._is_valid_request_ids(data["patient_id"], data["doctor_id"])

        ## 희망 예약 진료 시각에 대하여 해당 의사가 진료가 가능한지 확인
        book_time = datetime(
            data["year"],
            data["month"],
            data["day"],
            data["hour"],
            data["min"],
        )
        no = book_time.isoweekday()

        if no < 6:
            # 진료 요청일이 평일인 경우
            queryset = WeekDayTime.objects.filter(doctor=data["doctor_id"])

            objs = queryset.filter(
                Q(to_hour__gte=data["hour"], lunch_to__lt=data["hour"])
                | Q(lunch_from__gt=data["hour"], from_hour__lte=data["hour"])
            ).values_list("from_hour", "lunch_from", "lunch_to", "to_hour")
        else:
            # 진료 요청일이 주말인 경우
            queryset = WeekendTime.objects.filter(
                doctor=data["doctor_id"], closed=False
            )

            objs = queryset.filter(
                to_hour__gte=data["hour"], from_hour__lte=data["hour"]
            ).values_list("from_hour", "to_hour")

        if objs:
            # 진료 예약이 가능하다면 요청 만료 시각 계산
            # now = datetime.now()
            now = datetime(2022, 1, 15, 1, 0)
            hour_range_list = list(objs.first())
            datetime_objs_list = (
                self._convert_hour_list_to_datetime_object_list(
                    hour_range_list, now
                )
            )

            (
                is_workday_weekday,
                is_workday_weekend,
                is_lunch_time,
            ) = self._set_conditions(datetime_objs_list, now)

            if is_workday_weekday or is_workday_weekend:
                # 현재 의사가 부재중이 아닌 경우
                # 요청 만료 시각은 현시점으로부터 20분 후
                info = {
                    "patient": data["patient_id"],
                    "doctor": data["doctor_id"],
                    "book_time": book_time,
                    "expire_time": now + timedelta(minutes=20),
                }
            else:
                # 현재 의사가 부재중인 경우 가장 가까운 다음 영업일을 찾는다.
                if is_lunch_time:
                    # 점심 시간으로 인한 부재
                    info = {
                        "patient": data["patient_id"],
                        "doctor": data["doctor_id"],
                        "book_time": book_time,
                        "expire_time": datetime(now.year, now.month, now.day)
                        + timedelta(hours=hour_range_list[2], minutes=15),
                    }
                else:
                    # 금일 영업시간 종료로 인한 부재
                    info = {
                        "patient": data["patient_id"],
                        "doctor": data["doctor_id"],
                        "book_time": book_time,
                        "expire_time": datetime(
                            now.year, now.month, now.day + 1
                        )
                        + timedelta(hours=hour_range_list[0], minutes=15),
                    }
            serializer = self.get_serializer(data=info)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        else:
            return Response(
                {"message": "진료 예약이 불가능합니다. 다른 시간을 선택해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from django.db.models import Q

import json
from ..models import WeekDayTime, WeekendTime, CareRequestList
from ..serializers import (
    CareRequestSerializer,
    CareRequestListSerializer,
)
from ..utils.internal_functions import *
from datetime import datetime, timedelta


class CareRequestView(ListAPIView):
    queryset = CareRequestList.objects.all()
    serializer_class = CareRequestSerializer

    def get(self, request, *args, **kwargs):
        """
        한 의사의 모든 진료 요청을 검색합니다.
        input : 의사 id
        output : 특정 의사의 진료 예약 요청 리스트
        """
        doctor_id = request.GET.get("id", None)
        is_valid_request_ids(None, doctor_id)

        results = (
            self.get_queryset()
            .select_related("patient")
            .filter(doctor=doctor_id, is_booked=False)
        )

        serializer = CareRequestListSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        환자가 의사에게 진료 예약 요청을 전송합니다.
        input : 환자 id, 의사 id, 희망 진료 시각(년/월/일/시/분)
        output : CareRequestSerializer
        """
        data = json.loads(request.body)
        is_valid_request_ids(data["patient_id"], data["doctor_id"])

        ## 희망 예약 진료 시각에 대하여 해당 의사가 진료가 가능한지 확인
        now = datetime.now()
        book_time = datetime(
            data["year"],
            data["month"],
            data["day"],
            data["hour"],
            data["min"],
        )
        if now > book_time:
            return Response(
                {"message": "진료 예약이 불가능합니다. 다른 시간을 선택해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
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
            hour_range_list = list(objs.first())
            datetime_objs_list = convert_hour_list_to_datetime_object_list(
                hour_range_list, now
            )

            (
                is_workday_weekday,
                is_workday_weekend,
                is_lunch_time,
            ) = set_conditions(datetime_objs_list, now)

            info = {
                "patient": data["patient_id"],
                "doctor": data["doctor_id"],
                "book_time": book_time,
            }

            if is_workday_weekday or is_workday_weekend:
                # 현재 의사가 부재중이 아닌 경우
                # 요청 만료 시각은 현시점으로부터 20분 후
                info.update(
                    {
                        "expire_time": now + timedelta(minutes=20),
                    }
                )
            else:
                # 현재 의사가 부재중인 경우 가장 가까운 다음 영업일을 찾는다.
                if is_lunch_time:
                    # 점심 시간으로 인한 부재
                    info.update(
                        {
                            "expire_time": datetime(
                                now.year, now.month, now.day
                            )
                            + timedelta(hours=hour_range_list[2], minutes=15),
                        }
                    )
                else:
                    # 금일 영업시간 종료로 인한 부재
                    # 주말에 영업을 하지 않는 의사에 대한 다음 영업일 찾기
                    obj = WeekDayTime.objects.filter(
                        doctor=data["doctor_id"]
                    ).values_list("weekday_from", "weekday_to")
                    working_day_list = list(obj.first())
                    step = get_next_working_day(working_day_list, now)

                    info.update(
                        {
                            "expire_time": datetime(
                                now.year, now.month, now.day + step
                            )
                            + timedelta(hours=hour_range_list[0], minutes=15),
                        }
                    )
            serializer = self.get_serializer(data=info)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(
                {"message": "진료 예약이 불가능합니다. 다른 시간을 선택해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def patch(self, request, id):
        """
        의사가 특정 진료 요청을 수락합니다.
        input : 진료 요청 id
        output : CareRequestSerializer
        """
        try:
            obj = self.get_queryset().get(id=id)
        except CareRequestList.DoesNotExist:
            return Response(
                {"message": "해당 진료 요청이 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if obj.is_booked == False:
            now = datetime.now()
            if now > obj.expire_time:
                return Response(
                    {"message": "예약 요청이 만료되었습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            data = {"is_booked": True}
            serializer = self.get_serializer(obj, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response(
                {"message": "이미 수락된 예약입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

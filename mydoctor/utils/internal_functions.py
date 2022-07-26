from ..models import Doctor, Patient
from django.shortcuts import get_object_or_404

from datetime import datetime, timedelta
from typing import Dict, List


def is_valid_request_ids(p_id, d_id) -> None:
    ## 환자 id, 의사 id 예외 처리
    patient = get_object_or_404(Patient, id=p_id) if p_id else None
    doctor = get_object_or_404(Doctor, id=d_id) if d_id else None


def convert_hour_list_to_datetime_object_list(hour_list, now) -> List[datetime]:
    # ex) [9, 12, 13, 18] -> [09:00, 12:00, 13:00, 18:00]
    res = []
    for hour in hour_list:
        res.append(
            datetime(now.year, now.month, now.day) + timedelta(hours=hour)
        )
    return res


def set_conditions(datetime_objs_list, now) -> bool:
    if len(datetime_objs_list) > 2:
        # 평일 조건
        is_workday_weekday = (
            datetime_objs_list[0] <= now < datetime_objs_list[1]
            or datetime_objs_list[2] <= now < datetime_objs_list[3]
        )
        is_lunch_time = datetime_objs_list[1] <= now < datetime_objs_list[2]
        is_workday_weekend = False
    else:
        # 주말 조건
        is_workday_weekday = False
        is_workday_weekend = (
            datetime_objs_list[0] <= now < datetime_objs_list[1]
        )
        is_lunch_time = False
    return is_workday_weekday, is_workday_weekend, is_lunch_time


def get_next_working_day(working_day_list, now) -> int:
    # 다음 영업일이 요청 시점으로 부터 얼마나 떨어져있는지 계산
    # 영업일 범위가 [1(월), 5(금)]인 경우,
    # 요청 시점이 범위내에 있다면 step의 값은 1
    # 요청 시점이 금요일 영업시간 이후의 요청인 경우
    # step의 값은 3
    now_no = now.isoweekday()
    if working_day_list[0] <= now_no < working_day_list[1]:
        step = 1
    else:
        # 다음날 영업을 하지 않는 경우
        step = 1
        while True:
            if now_no == 7:
                now_no = 1
            if working_day_list[0] <= now_no < working_day_list[1]:
                break
            step += 1
            now_no += 1
    return step

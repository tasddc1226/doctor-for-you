from datetime import datetime
from django.db import models
from django_mysql.models import ListCharField
from django.utils.translation import gettext as _

WEEKDAYS = [
    (1, _("Monday")),
    (2, _("Tuesday")),
    (3, _("Wednesday")),
    (4, _("Thursday")),
    (5, _("Friday")),
]
WEEKENDS = [
    (6, _("Saturday")),
    (7, _("Sunday")),
]
HOUR_OF_DAY_24 = [(i, i) for i in range(1, 25)]


class Patient(models.Model):
    name = models.CharField(max_length=64, verbose_name="환자 이름")

    class Meta:
        db_table = "patient"


class Doctor(models.Model):
    name = models.CharField(max_length=64, verbose_name="의사 이름")
    hospital = models.CharField(max_length=64, verbose_name="소속 병원 이름")
    dept = ListCharField(
        base_field=models.CharField(max_length=10),
        size=16,
        max_length=(16 * 11),
        verbose_name="진료과",
    )
    non_paid = models.CharField(
        max_length=64, null=True, blank=True, verbose_name="비급여진료과목"
    )

    class Meta:
        db_table = "doctor"


class CareRequestList(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, verbose_name="환자 id"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, verbose_name="의사 id"
    )
    book_time = models.DateTimeField(verbose_name="희망 진료 시각")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="예약 요청 시각"
    )
    expire_time = models.DateTimeField(verbose_name="요청 만료 시각")
    is_booked = models.BooleanField(default=False, verbose_name="진료 요청 수락 여부")

    class Meta:
        db_table = "care"


class WeekDayTime(models.Model):
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, verbose_name="의사"
    )
    weekday_from = models.PositiveSmallIntegerField(
        choices=WEEKDAYS, verbose_name="영업 시작 요일"
    )
    weekday_to = models.PositiveSmallIntegerField(
        choices=WEEKDAYS, verbose_name="영업 종료 요일"
    )
    from_hour = models.PositiveSmallIntegerField(
        choices=HOUR_OF_DAY_24, verbose_name="영업 시작 시각"
    )
    to_hour = models.PositiveSmallIntegerField(
        choices=HOUR_OF_DAY_24, verbose_name="영업 종료 시각"
    )
    lunch_from = models.PositiveSmallIntegerField(
        choices=HOUR_OF_DAY_24, verbose_name="점심 시작 시각"
    )
    lunch_to = models.PositiveSmallIntegerField(
        choices=HOUR_OF_DAY_24, verbose_name="점심 종료 시각"
    )

    class Meta:
        db_table = "weekday"


class WeekendTime(models.Model):
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, verbose_name="의사"
    )
    holiday = models.PositiveSmallIntegerField(
        choices=WEEKENDS, verbose_name="주말 요일"
    )
    closed = models.BooleanField(default=True, verbose_name="휴일 유무")
    from_hour = models.PositiveSmallIntegerField(
        choices=HOUR_OF_DAY_24, null=True, blank=True, verbose_name="영업 시작 시각"
    )
    to_hour = models.PositiveSmallIntegerField(
        choices=HOUR_OF_DAY_24, null=True, blank=True, verbose_name="영업 종료 시각"
    )

    class Meta:
        db_table = "weekend"

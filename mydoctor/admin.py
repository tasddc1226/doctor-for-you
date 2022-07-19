from django.contrib import admin
from .models import Patient, Doctor, WeekDayTime, WeekendTime, CareRequestList

# Register your models here.
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(WeekDayTime)
admin.site.register(WeekendTime)
admin.site.register(CareRequestList)

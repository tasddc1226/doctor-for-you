from django.urls import path

from .views import DoctorSeaerchView, CareRequestView

urlpatterns = [
    path("search/", DoctorSeaerchView.as_view(), name="search doctor"),
    path("care/", CareRequestView.as_view(), name="care request"),
]

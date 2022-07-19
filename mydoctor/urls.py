from django.urls import path

from .views import DoctorSeaerchView

urlpatterns = [
    path("search/", DoctorSeaerchView.as_view(), name="search doctor")
]

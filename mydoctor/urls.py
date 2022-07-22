from django.urls import path

from .views import DoctorSeaerchView, CareRequestView

urlpatterns = [
    path("search/", DoctorSeaerchView.as_view(), name="search doctor"),
    path("cares/", CareRequestView.as_view(), name="care request"),
    path(
        "cares/<int:id>", CareRequestView.as_view(), name="care request accept"
    ),
]

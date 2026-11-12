from django.urls import path

from . import views

urlpatterns = [
    path("sessions/<int:session_id>/", views.session_attestations, name="session_attestations"),
    path("<int:pk>/telecharger/", views.download_attestation, name="download_attestation"),
]

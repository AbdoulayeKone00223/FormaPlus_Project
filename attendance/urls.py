from django.urls import path

from . import views

urlpatterns = [
    path("sessions/<int:session_id>/presences/", views.presence_sheet, name="presence_sheet"),
    path("sessions/<int:session_id>/evaluations/", views.evaluation_sheet, name="evaluation_sheet"),
]

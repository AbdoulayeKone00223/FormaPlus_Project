from django.urls import path

from . import views

urlpatterns = [
    path("", views.inscription_list, name="inscription_list"),
    path("sessions/<int:session_id>/inscrire/", views.enroll, name="enroll"),
    path("<int:pk>/annuler/", views.cancel_enrollment, name="cancel_enrollment"),
    path("<int:pk>/paiement/", views.paiement_create, name="paiement_create"),
]

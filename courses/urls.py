from django.urls import path

from . import views

urlpatterns = [
    path("", views.formation_list, name="formation_list"),
    path("<int:pk>/", views.formation_detail, name="formation_detail"),
]

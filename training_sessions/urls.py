from django.urls import path

from . import views

urlpatterns = [
    path("", views.session_list, name="session_list"),
    path("<int:pk>/", views.session_detail, name="session_detail"),
]

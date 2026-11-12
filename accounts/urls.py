from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import ConnexionForm

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("demo/<str:role>/", views.demo_login, name="demo_login"),
    path(
        "connexion/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=ConnexionForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
    path("inscription/", views.register, name="register"),
]

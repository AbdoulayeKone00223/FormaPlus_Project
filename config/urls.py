from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "FormaPlus - Administration"
admin.site.site_title = "FormaPlus"
admin.site.index_title = "Gestion du centre de formation"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("formations/", include("courses.urls")),
    path("sessions/", include("training_sessions.urls")),
    path("inscriptions/", include("enrollments.urls")),
    path("suivi/", include("attendance.urls")),
    path("attestations/", include("certificates.urls")),
    path("", include("accounts.urls")),
]

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from sams import settings

from .views import back, home

app_name = "sams"

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("", home, name="home"),
        path("home", home, name="home"),
        path("back", back, name="back"),
        path("accounts/", include("account.urls")),
        path("doctors/", include("doctor.urls")),
        path("receptionists/", include("receptionist.urls")),
        path("students/", include("student.urls")),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import index
from sams import settings

app_name = "sams"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="index"),
    path('account/', include("account.urls")),
    path('doctor/', include("doctor.urls")),
    path('receptionist/', include("receptionist.urls")),
    path('student/', include("student.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



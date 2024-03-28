from django.conf.urls.static import static
from django.urls import path
from .views import home
from sams import settings

app_name = "doctor"

urlpatterns = [
    path('home/', home, name="doctor-home"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
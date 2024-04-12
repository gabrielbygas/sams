from django.conf.urls.static import static
from django.urls import path
from .views import home
from sams import settings

app_name = "receptionists"

urlpatterns = [
    path('home/', home, name="receptionist-home"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.conf.urls.static import static
from django.urls import path
from .views import home, get_doctors
from sams import settings

app_name = "doctors"

urlpatterns = [
    path('home/', home, name="home"),
    path('get_doctors/', get_doctors, name="get_doctors"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
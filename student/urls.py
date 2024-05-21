from django.conf.urls.static import static
from django.urls import path
from .views import home, AppointmentCreateView, AppointmentListView, student_error_page
from sams import settings

app_name = "students"

urlpatterns = [
    path('', home, name="home"),
    path('appointment/create/', AppointmentCreateView.as_view(), name="create-appointment"),
    path('appointment/list/', AppointmentListView.as_view(), name="list-appointment"),
    path('error-page/', student_error_page, name="error-page"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
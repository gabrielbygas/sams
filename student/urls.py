from django.conf.urls.static import static
from django.urls import path
from .views import home, AppointmentCreateView, AppointmentListView, AppointmentDetailView, AppointmentUpdateView, AppointmentDeleteView, student_error_page
from sams import settings

app_name = "students"

urlpatterns = [
    path('', home, name="home"),
    path('appointment/create/', AppointmentCreateView.as_view(), name="create-appointment"),
    path('appointment/list/', AppointmentListView.as_view(), name="list-appointment"),
    path('appointment/view/<int:pk>/', AppointmentDetailView.as_view(), name="view-appointment"),
    path('appointment/update/<int:pk>/', AppointmentUpdateView.as_view(), name="update-appointment"),
    path('appointment/delete/<int:pk>/', AppointmentDeleteView.as_view(), name="delete-appointment"),
    path('error-page/', student_error_page, name="error-page"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
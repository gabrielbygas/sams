from django.conf.urls.static import static
from django.urls import path
from .views import home, AppointmentCreateView, AppointmentListView, AppointmentDetailView, AppointmentUpdateView, AppointmentDeleteView, student_error_page, EnquiryCreateView, EnquiryListView, EnquiryDetailView, EnquiryUpdateView, EnquiryDeleteView
from sams import settings

app_name = "students"

urlpatterns = [
    path('', home, name="home"),
    path('appointment/create/', AppointmentCreateView.as_view(), name="create-appointment"),
    path('appointment/list/', AppointmentListView.as_view(), name="list-appointment"),
    path('appointment/view/<int:pk>/', AppointmentDetailView.as_view(), name="view-appointment"),
    path('appointment/update/<int:pk>/', AppointmentUpdateView.as_view(), name="update-appointment"),
    path('appointment/delete/<int:pk>/', AppointmentDeleteView.as_view(), name="delete-appointment"),
    path('enquiry/create/', EnquiryCreateView.as_view(), name="create-enquiry"),
    path('enquiry/list/', EnquiryListView.as_view(), name="list-enquiry"),
    path('enquiry/view/<int:pk>/', EnquiryDetailView.as_view(), name="view-enquiry"),
    path('enquiry/update/<int:pk>/', EnquiryUpdateView.as_view(), name="update-enquiry"),
    path('enquiry/delete/<int:pk>/', EnquiryDeleteView.as_view(), name="delete-enquiry"),
    path('error-page/', student_error_page, name="error-page"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
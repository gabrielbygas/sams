from django.conf.urls.static import static
from django.urls import path
from sams import settings
from .views import home, get_doctors, EnquiryListView, EnquiryListAllView, EnquiryUpdateView, EnquiryDetailView, AppointmentListView, AppointmentDetailView

app_name = "doctors"

urlpatterns = [
    path('home/', home, name="home"),
    path('', home, name="home"),
    path('get_doctors/', get_doctors, name="get_doctors"),
    path('enquiry/list/', EnquiryListView.as_view(), name="list-enquiry"),
    path('enquiry/list/all/', EnquiryListAllView.as_view(), name="list-enquiry-all"),
    path('enquiry/update/<int:pk>/', EnquiryUpdateView.as_view(), name="update-enquiry"),
    path('enquiry/view/<int:pk>/', EnquiryDetailView.as_view(), name="view-enquiry"),
    path('appointment/list/', AppointmentListView.as_view(), name="list-appointment"),
    path('appointment/view/<int:pk>/', AppointmentDetailView.as_view(), name="view-appointment"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
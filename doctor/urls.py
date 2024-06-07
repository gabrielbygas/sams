from django.conf.urls.static import static
from django.urls import path
from .views import home, get_doctors, EnquiryListView, EnquiryListAnsweredView, EnquiryUpdateView
from sams import settings

app_name = "doctors"

urlpatterns = [
    path('home/', home, name="home"),
    path('', home, name="home"),
    path('get_doctors/', get_doctors, name="get_doctors"),
    path('enquiry/list/', EnquiryListView.as_view(), name="list-enquiry"),
    path('enquiry/list/answered', EnquiryListAnsweredView.as_view(), name="list-enquiry-answered"),
    path('enquiry/update/<int:pk>/', EnquiryUpdateView.as_view(), name="update-enquiry"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
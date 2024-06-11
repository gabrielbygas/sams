from django.conf.urls.static import static
from django.urls import path
from .views import home, AnnouncementCreateView, AnnouncementDeleteView, AnnouncementDetailView, AnnouncementListView, AnnouncementUpdateView
from sams import settings

app_name = "receptionists"

urlpatterns = [
    path('home/', home, name="home"),
    path('', home, name="home"),
    path('announcement/create/', AnnouncementCreateView.as_view(), name="create-announcement"),
    path('announcement/list/', AnnouncementListView.as_view(), name="list-announcement"),
    path('announcement/view/<int:pk>/', AnnouncementDetailView.as_view(), name="view-announcement"),
    path('announcement/update/<int:pk>/', AnnouncementUpdateView.as_view(), name="update-announcement"),
    path('announcement/delete/<int:pk>/', AnnouncementDeleteView.as_view(), name="delete-announcement"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
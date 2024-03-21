from django.conf.urls.static import static
from django.urls import path
from .views import login, logout
from sams import settings

app_name = "account"

urlpatterns = [
    path('login/', login, name="account-login"),
    path('logout/', logout, name="account-logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


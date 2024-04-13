from django.conf.urls.static import static
from django.urls import path
from .views import auth_login, auth_logout, create_doctor, create_receptionist, create_student, user_creation_error_page
from sams import settings

app_name = "accounts"

urlpatterns = [
    path('login/', auth_login, name="login"),
    path('logout/', auth_logout, name="logout"),
    path('create-doctor/', create_doctor, name="create-doctor"),
    path('create-receptionist/', create_receptionist, name="create-receptionist"),
    path('create-student/', create_student, name="create-student"),
    path('user_creation_error_page/', user_creation_error_page, name="user_creation_error_page")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.users import views

urlpatterns = [

    # Authentication
    path("register/", views.create_user, name="register_user"),
    path("login/", views.login_user, name="login_user"),

    # OTP
    path("otp/send/", views.send_otp, name="send_otp"),
    path("otp/verify/", views.verify_otp, name="verify_otp"),

    # Users listing
    path("", views.get_all_users, name="get_all_users"),
    path("role/<str:role>/", views.get_users_by_role, name="get_users_by_role"),
   

    # Admin user management
    path("admin/create/", views.admin_create_user, name="admin_create_user"),
    path("admin/<int:user_id>/update/", views.admin_update_user, name="admin_update_user"),
    path("admin/<int:user_id>/delete/", views.admin_delete_user, name="admin_delete_user"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





#     POST   /api/users/register/
# POST   /api/users/login/

# POST   /api/users/otp/send/
# POST   /api/users/otp/verify/

# GET    /api/users/
# GET    /api/users/role/student/
# GET    /api/users/role/teacher/

# POST   /api/users/admin/create/
# PUT    /api/users/admin/5/update/
# DELETE /api/users/admin/5/delete/
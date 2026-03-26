from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),

    path('admin/', admin.site.urls),

    # ✅ CORRECT APPS
    path('api/assignments/', include('apps.assignments.urls')),
    path('api/courses/', include('apps.courses.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/attendance/',include('apps.attendance.urls')),
]

# ✅ MEDIA FILES
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
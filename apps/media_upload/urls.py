from django.urls import path
from .views import single_upload, multiple_upload

urlpatterns = [
    path("upload/single/", single_upload),
    path("upload/multiple/", multiple_upload),
]

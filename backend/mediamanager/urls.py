from django.urls import path, re_path
from . import views

app_name = "mediamanager"

urlpatterns = [
    path('upload/cdr/', views.CDRUploadView.as_view(), name="uploadview"),
    path('upload/ipdr/', views.IPDRUploadView.as_view(), name="uploadview"),
    # path('', views.MediaRedirect.as_view()),
]

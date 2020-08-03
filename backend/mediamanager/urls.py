from django.urls import path, re_path
from . import views

app_name = "mediamanager"

urlpatterns = [
    path('upload/cdr/', views.CDRUploadView.as_view(), name="uploadview"),
    path('upload/ipdr/', views.IPDRUploadView.as_view(), name="uploadview"),
    path('upload/speech/', views.SpeechUploadView.as_view(), name="speehupload"),
    # path('upload/persondetect/', views.PersonDetectionUploadView.as_view(), name="speehupload"),

    # path('', views.MediaRedirect.as_view()),
]

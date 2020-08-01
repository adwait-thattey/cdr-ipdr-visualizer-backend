from django.urls import path, re_path
from . import views

app_name = "mediamanager"

urlpatterns = [
    path('upload/', views.MediaManagerView.as_view(), name="uploadview")
    # path('', views.MediaRedirect.as_view()),
]

from django.urls import path, re_path
from . import views

app_name = "data"

urlpatterns = [
    path('', views.FullCDRView.as_view(),  name="dataview")
    # path('', views.MediaRedirect.as_view()),
]

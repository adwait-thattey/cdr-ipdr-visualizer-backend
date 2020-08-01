from django.urls import path, re_path
from . import views

app_name = "data"

urlpatterns = [
    path('', views.MinimalCombinedView.as_view(), name="dataview"),
    path('cdrs/', views.FullCDRView.as_view(), name="fullcdrview"),
    path('persons/', views.DetailedPersonView.as_view(), name="full persons view")
    # path('', views.MediaRedirect.as_view()),
]

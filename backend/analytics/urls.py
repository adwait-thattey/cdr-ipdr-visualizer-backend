from django.urls import path, re_path
from . import views

app_name = "analytics"

urlpatterns = [
    path('community/', views.CommunityGraphView.as_view(), name="community"),
    # path('', views.MediaRedirect.as_view()),
]

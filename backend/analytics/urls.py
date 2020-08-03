from django.urls import path, re_path
from . import views

app_name = "analytics"

urlpatterns = [
    path('community/', views.CommunityGraphView.as_view(), name="community"),
    path('similarnumbers/<number>', views.SimilarNumbersView.as_view(), name="similar_number"),
    path('spammers/', views.SpammersView.as_view(), name="spammer")
    # path('', views.MediaRedirect.as_view()),
]

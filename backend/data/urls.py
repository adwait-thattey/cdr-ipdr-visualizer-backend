from django.urls import path, re_path
from . import views

app_name = "data"

urlpatterns = [
    path('', views.MinimalCombinedView.as_view(), name="dataview"),
    path('cdrs/', views.FullCDRView.as_view(), name="fullcdrview"),
    path('ipdrs/', views.FullIPDRView.as_view(), name="fullipdrview"),
    path('persons/', views.DetailedPersonView.as_view(), name="full persons view"),
    path('watchlists/', views.WatchListView.as_view(), name="watchlist_view"),
    path('timeline/users/<user_id>/', views.UserTimelineView.as_view(), name="user timeline"),
    path('services/', views.ServiceView.as_view(), name="service view")
    # path('', views.MediaRedirect.as_view()),
]

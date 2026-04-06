from django.urls import path
from .views import RecordListCreateView, RecordDetailView

urlpatterns = [
    path("", RecordListCreateView.as_view(), name="record-list"),
    path("<uuid:pk>/", RecordDetailView.as_view(), name="record-detail"),
]

from django.urls import path
from .views import DashboardSummaryView, DashboardCategoriesView, DashboardTrendsView, DashboardRecentView

urlpatterns = [
    path("summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("categories/", DashboardCategoriesView.as_view(), name="dashboard-categories"),
    path("trends/", DashboardTrendsView.as_view(), name="dashboard-trends"),
    path("recent/", DashboardRecentView.as_view(), name="dashboard-recent"),
]

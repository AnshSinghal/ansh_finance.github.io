from django.urls import path
from .views import MeView, UserListView, UserDetailView, UserRoleUpdateView

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("me/", MeView.as_view(), name="user-me"),
    path("<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("<uuid:pk>/role/", UserRoleUpdateView.as_view(), name="user-role"),
]

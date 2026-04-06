from rest_framework.permissions import BasePermission
from .models import Role


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.ADMIN)


class IsAnalystOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (Role.ANALYST, Role.ADMIN)
        )


class IsAnyRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

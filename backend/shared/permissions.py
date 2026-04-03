from rest_framework.permissions import BasePermission
from apps.accounts.models import UserRole


class IsSystemAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == UserRole.SYSTEM_ADMIN)


class IsFieldAgentOrAbove(BasePermission):
    ALLOWED = [
        UserRole.FIELD_AGENT, UserRole.SUPERVISOR,
        UserRole.ANALYST, UserRole.SYSTEM_ADMIN, UserRole.EXECUTIVE,
    ]

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in self.ALLOWED)


class IsSupervisorOrAbove(BasePermission):
    ALLOWED = [UserRole.SUPERVISOR, UserRole.SYSTEM_ADMIN, UserRole.EXECUTIVE]

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in self.ALLOWED)


class IsAnalystOrAbove(BasePermission):
    ALLOWED = [
        UserRole.ANALYST, UserRole.SUPERVISOR,
        UserRole.SYSTEM_ADMIN, UserRole.EXECUTIVE,
    ]

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in self.ALLOWED)


class IsPartnerUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == UserRole.PARTNER_USER)


class IsPartnerOrAbove(BasePermission):
    """Partner users plus internal staff."""
    ALLOWED = [
        UserRole.PARTNER_USER, UserRole.ANALYST, UserRole.SUPERVISOR,
        UserRole.SYSTEM_ADMIN, UserRole.EXECUTIVE,
    ]

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in self.ALLOWED)


class IsExecutive(BasePermission):
    ALLOWED = [UserRole.EXECUTIVE, UserRole.SYSTEM_ADMIN]

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in self.ALLOWED)

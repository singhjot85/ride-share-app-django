"""
Role-based permissions derived from User flags.
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class BaseUserRolePermission(BasePermission):
    """
    Base permission checking that the request user is authenticated, active, and has a specific role flag.
    """

    role_flag: str = ""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if the request user is authenticated, active, and has the role flag set.
        """
        user = getattr(request, "user", None)
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "is_active", False)
            and getattr(user, self.role_flag, False)
        )


class IsAuthenticatedDriver(BaseUserRolePermission):
    """
    Allows access only to authenticated, active drivers.
    """

    role_flag = "is_driver"
    message = "User is not registered as a driver."


class IsAuthenticatedBooker(BaseUserRolePermission):
    """
    Allows access only to authenticated, active bookers/senders.
    """

    role_flag = "is_booker"
    message = "User is not registered as a booker."

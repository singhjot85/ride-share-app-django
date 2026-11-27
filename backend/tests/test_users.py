"""
Unit and integration tests for the host Users app, swapped model, and role permissions.
"""

import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

from apps.users import get_user_model
from apps.users.permissions import (
    IsAuthenticatedBooker,
    IsAuthenticatedDriver,
)

User = get_user_model()


@pytest.fixture
def api_factory():
    """Return DRF APIRequestFactory for permission tests."""
    return APIRequestFactory()


@pytest.fixture
def regular_user(db):
    """Create an active user with neither driver nor booker role."""
    return User.objects.create_user(
        username="regular_user",
        email="regular@example.com",
        phone_number="+919876543220",
        is_active=True,
    )


@pytest.fixture
def driver_user(db):
    """Create an active user with is_driver=True."""
    return User.objects.create_user(
        username="driver_user",
        email="driver@example.com",
        phone_number="+919876543221",
        is_active=True,
        is_driver=True,
    )


@pytest.fixture
def booker_user(db):
    """Create an active user with is_booker=True."""
    return User.objects.create_user(
        username="booker_user",
        email="booker@example.com",
        phone_number="+919876543222",
        is_active=True,
        is_booker=True,
    )


@pytest.fixture
def dual_role_user(db):
    """Create an active user with both is_driver=True and is_booker=True."""
    return User.objects.create_user(
        username="dual_user",
        email="dual@example.com",
        phone_number="+919876543223",
        is_active=True,
        is_driver=True,
        is_booker=True,
    )


@pytest.fixture
def inactive_driver_user(db):
    """Create an inactive user with is_driver=True."""
    return User.objects.create_user(
        username="inactive_driver",
        email="inactive_driver@example.com",
        phone_number="+919876543224",
        is_active=False,
        is_driver=True,
    )


@pytest.fixture
def inactive_booker_user(db):
    """Create an inactive user with is_booker=True."""
    return User.objects.create_user(
        username="inactive_booker",
        email="inactive_booker@example.com",
        phone_number="+919876543225",
        is_active=False,
        is_booker=True,
    )


class TestUserModel:
    """Tests for the swapped host User model."""

    def test_user_model_is_host_model(self):
        """Assert dynamic getter resolves the host User model."""
        assert User.__module__ == "apps.users.models"

    def test_user_flags_default_to_false(self, regular_user):
        """Assert is_driver and is_booker default to False."""
        assert regular_user.is_driver is False
        assert regular_user.is_booker is False

    def test_create_driver_user(self, driver_user):
        """Assert user can be created with is_driver=True."""
        assert driver_user.is_driver is True
        assert driver_user.is_booker is False

    def test_create_booker_user(self, booker_user):
        """Assert user can be created with is_booker=True."""
        assert booker_user.is_driver is False
        assert booker_user.is_booker is True

    def test_create_dual_role_user(self, dual_role_user):
        """Assert user can have both driver and booker flags set to True."""
        assert dual_role_user.is_driver is True
        assert dual_role_user.is_booker is True


class TestIsAuthenticatedDriverPermission:
    """Tests for the IsAuthenticatedDriver permission class."""

    def test_anonymous_user_denied(self, api_factory):
        """Assert unauthenticated user is denied."""
        request = api_factory.get("/")
        request.user = AnonymousUser()
        permission = IsAuthenticatedDriver()
        assert permission.has_permission(request, None) is False

    def test_regular_user_denied(self, api_factory, regular_user):
        """Assert authenticated user without is_driver is denied."""
        request = api_factory.get("/")
        request.user = regular_user
        permission = IsAuthenticatedDriver()
        assert permission.has_permission(request, None) is False

    def test_driver_user_allowed(self, api_factory, driver_user):
        """Assert authenticated active driver is granted access."""
        request = api_factory.get("/")
        request.user = driver_user
        permission = IsAuthenticatedDriver()
        assert permission.has_permission(request, None) is True

    def test_dual_role_user_allowed(self, api_factory, dual_role_user):
        """Assert user with both roles is granted driver access."""
        request = api_factory.get("/")
        request.user = dual_role_user
        permission = IsAuthenticatedDriver()
        assert permission.has_permission(request, None) is True

    def test_inactive_driver_denied(self, api_factory, inactive_driver_user):
        """Assert inactive driver user is denied."""
        request = api_factory.get("/")
        request.user = inactive_driver_user
        permission = IsAuthenticatedDriver()
        assert permission.has_permission(request, None) is False


class TestIsAuthenticatedBookerPermission:
    """Tests for the IsAuthenticatedBooker permission class."""

    def test_anonymous_user_denied(self, api_factory):
        """Assert unauthenticated user is denied."""
        request = api_factory.get("/")
        request.user = AnonymousUser()
        permission = IsAuthenticatedBooker()
        assert permission.has_permission(request, None) is False

    def test_regular_user_denied(self, api_factory, regular_user):
        """Assert authenticated user without is_booker is denied."""
        request = api_factory.get("/")
        request.user = regular_user
        permission = IsAuthenticatedBooker()
        assert permission.has_permission(request, None) is False

    def test_booker_user_allowed(self, api_factory, booker_user):
        """Assert authenticated active booker is granted access."""
        request = api_factory.get("/")
        request.user = booker_user
        permission = IsAuthenticatedBooker()
        assert permission.has_permission(request, None) is True

    def test_dual_role_user_allowed(self, api_factory, dual_role_user):
        """Assert user with both roles is granted booker access."""
        request = api_factory.get("/")
        request.user = dual_role_user
        permission = IsAuthenticatedBooker()
        assert permission.has_permission(request, None) is True

    def test_inactive_booker_denied(self, api_factory, inactive_booker_user):
        """Assert inactive booker user is denied."""
        request = api_factory.get("/")
        request.user = inactive_booker_user
        permission = IsAuthenticatedBooker()
        assert permission.has_permission(request, None) is False

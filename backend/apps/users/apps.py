"""
Application configuration for the host Users app inheriting core setup.
"""

from core.apps.users.apps import UsersConfig as CoreUsersConfig


class UsersConfig(CoreUsersConfig):
    """
    AppConfig for the host-level Users application with label 'users'.
    """

    name = "apps.users"

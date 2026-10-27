"""
AppConfig definition for the overrides application.
"""

from django.apps import AppConfig


class OverridesConfig(AppConfig):
    """
    Application configuration for project-specific view and template overrides.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "overrides"
    verbose_name = "Host Overrides"

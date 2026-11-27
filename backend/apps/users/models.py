"""
Concrete models for the host Users app declaring swappable setting targets.
"""

from core.apps.users.models_abstract import (
    AbstractOTPLog,
    AbstractSocialAccount,
    AbstractUser,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Concrete User model for the host application with driver and booker role support.
    """

    is_driver = models.BooleanField(
        _("Is Driver"),
        default=False,
        help_text=_("Designates whether the user is a registered vehicle driver."),
    )
    is_booker = models.BooleanField(
        _("Is Booker"),
        default=False,
        help_text=_("Designates whether the user is a parcel booker/sender."),
    )

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class SocialAccount(AbstractSocialAccount):
    """
    Concrete SocialAccount model linking third-party identity providers to a user.
    """

    class Meta(AbstractSocialAccount.Meta):
        swappable = "USERS_SOCIAL_ACCOUNT_MODEL"


class OTPLog(AbstractOTPLog):
    """
    Concrete OTPLog model for tracking verification attempts and delivery status.
    """

    class Meta(AbstractOTPLog.Meta):
        swappable = "USERS_OTP_LOG_MODEL"


__all__ = ["OTPLog", "SocialAccount", "User"]

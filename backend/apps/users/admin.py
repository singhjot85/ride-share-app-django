"""
Django admin configuration for the host Users application.
"""

from core.apps.users import get_user_model
from core.apps.users.admin import UserAdmin as CoreUserAdmin
from core.utils.admin import private_admin_site, public_admin_site
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserAdmin(CoreUserAdmin):
    """
    Host UserAdmin extending core's admin with driver and booker flags.
    """

    list_display = (*CoreUserAdmin.list_display, "is_driver", "is_booker")
    list_filter = (*CoreUserAdmin.list_filter, "is_driver", "is_booker")

    fieldsets = (
        *CoreUserAdmin.fieldsets[:2],
        (
            _("Roles & Flags"),
            {"fields": ("is_driver", "is_booker")},
        ),
        *CoreUserAdmin.fieldsets[2:],
    )


# Replace User registration on both private and public admin sites
for site in (public_admin_site, private_admin_site):
    if site.is_registered(User):
        site.unregister(User)
    site.register(User, UserAdmin)

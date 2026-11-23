"""
Development seeders for CRM application in the host project.
"""

from __future__ import annotations

from typing import Any

from core.apps.crm import (
    get_customer_model,
    get_customer_preference_model,
    get_customer_preference_type_model,
)
from core.apps.crm.fixtures.seeder import CustomerPreferenceTypeSeeder
from core.libraries.seeder import (
    BaseSeeder,
    FileBasedLoader,
    GetorCreateObject,
)
from core.libraries.seeder.registry import seeder_registry
from core.setup.crm.seeder import (
    DevCustomerAddressSeeder,
    DevCustomerEmailSeeder,
    DevCustomerPhoneSeeder,
)
from core.setup.invoices.seeder import DevInvoicePartySeeder
from django.conf import settings

from setup.users.seeders import DevUserSeeder

Customer = get_customer_model()
CustomerPreferenceType = get_customer_preference_type_model()
CustomerPreference = get_customer_preference_model()

# Unregister core DevCustomerSeeder so host project can register enhanced version with preferences
seeder_registry.unregister("dev_customer_seeder")


class DevCustomerPreferenceTypeSeeder(BaseSeeder):
    """Dev seeder for additional customer preference types (e.g. theme)."""

    schemas = [getattr(settings, "TENANT_TYPE_ORGANIZATION", "organization")]
    loader = FileBasedLoader(
        directory_name="setup/crm/customer_preference_type",
        load_method=FileBasedLoader.LOAD_INDIVIDUAL,
    )
    method = GetorCreateObject(
        model=CustomerPreferenceType,
        lookup_fields=["code"],
        default_fields=["label", "data_type", "default_value", "values"],
    )


class DevCustomerPreferenceSeeder(BaseSeeder):
    """Dev child seeder for customer preferences."""

    is_root: bool = False

    method = GetorCreateObject(
        model=CustomerPreference,
        lookup_fields=["customer", "preference_type"],
        default_fields=["value"],
    )

    def set_preference_type(self, raw_value: Any) -> Any:
        """Resolve preference_type by string code or $ref lookup."""
        PreferenceType = get_customer_preference_type_model()
        if isinstance(raw_value, str):
            return PreferenceType.objects.get(code=raw_value)
        if isinstance(raw_value, dict) and "$ref" in raw_value:
            return PreferenceType.objects.get(**raw_value["$ref"])
        return raw_value


class DevCustomerSeeder(BaseSeeder):
    """Dev root seeder for customers, coordinating nested attributes via related_seeder_map."""

    label = "dev_customer_seeder"
    depends_on = [
        CustomerPreferenceTypeSeeder,
        DevCustomerPreferenceTypeSeeder,
        DevUserSeeder,
    ]
    execution_order: int = 2
    schemas = [getattr(settings, "TENANT_TYPE_ORGANIZATION", "organization")]

    loader = FileBasedLoader(
        directory_name="setup/crm/dev_customer",
        load_method=FileBasedLoader.LOAD_INDIVIDUAL,
    )
    method = GetorCreateObject(
        model=Customer,
        related_seeder_map={
            "phones": DevCustomerPhoneSeeder,
            "emails": DevCustomerEmailSeeder,
            "addresses": DevCustomerAddressSeeder,
            "preferences": DevCustomerPreferenceSeeder,
        },
        lookup_fields=["first_name", "last_name"],
        default_fields=[
            "business_name",
            "customer_type",
            "status",
            "user",
            "phones",
            "emails",
            "addresses",
            "preferences",
        ],
    )


# Update DevInvoicePartySeeder to depend on host DevCustomerSeeder
DevInvoicePartySeeder.depends_on = [DevCustomerSeeder]

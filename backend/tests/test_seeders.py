"""
Unit tests validating host project database seeders and JSON setup configurations.
"""

import json
from pathlib import Path

import pytest
from core.apps.configurations.management.commands.run_dev_seeders import (
    auto_discover_seeders,
)
from core.apps.crm import (
    get_customer_address_model,
    get_customer_email_model,
    get_customer_model,
    get_customer_phone_model,
    get_customer_preference_model,
    get_customer_preference_type_model,
)
from core.apps.invoices import get_billing_organization_model
from core.libraries.seeder.runner import SeedDevelopmentData
from django.conf import settings
from django.contrib.auth import get_user_model

SETUP_DIR = Path(settings.BASE_DIR) / "setup"
CRM_CUSTOMER_FILES = list((SETUP_DIR / "crm" / "dev_customer").glob("*.json"))


def load_json(file_path: Path) -> list | dict:
    """Helper to parse a JSON file."""
    return json.loads(file_path.read_text(encoding="utf-8"))


class TestHostSetupJSONFiles:
    """Validate that all host project setup JSON files exist and are well-formed."""

    def test_tenants_json_valid(self):
        """Verify tenants.json defines the rideshare tenant with domain and type."""
        path = SETUP_DIR / "tenants" / "tenants.json"
        assert path.exists()
        data = load_json(path)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["schema_name"] == "rideshare"
        assert data[0]["domain"] == "rideshare.localhost"
        if "type" in data[0]:
            assert data[0]["type"] == "organization"

    def test_users_json_valid(self):
        """Verify users.json defines superuser and standard driver/sender users."""
        path = SETUP_DIR / "users" / "dev_users" / "users.json"
        assert path.exists()
        data = load_json(path)
        assert isinstance(data, list)
        user_map = {u["username"]: u for u in data}
        assert "admin" in user_map
        assert "driver_rajesh" in user_map
        assert "sender_priya" in user_map
        assert user_map["driver_rajesh"]["phone_number"] == "+919876543210"
        driver_pwd = user_map["driver_rajesh"]["password"]
        assert driver_pwd == "qwerty123"  # pragma: allowlist secret
        assert user_map["admin"].get("create_superuser") is True

    @pytest.mark.parametrize("file_path", CRM_CUSTOMER_FILES, ids=lambda p: p.stem)
    def test_crm_customer_json_file_valid(self, file_path: Path):
        """Verify individual customer JSON fixtures match the required schema."""
        record = load_json(file_path)
        assert record.get("status") in ("onboarding", "verified", "suspended")
        assert "$ref" in record.get("user", {})
        assert len(record.get("phones", [])) >= 1
        assert len(record.get("emails", [])) >= 1
        assert len(record.get("addresses", [])) >= 1
        assert len(record.get("preferences", [])) >= 1

    def test_crm_preference_type_json_valid(self):
        """Verify customer preference type theme JSON fixture is well-formed."""
        path = SETUP_DIR / "crm" / "customer_preference_type" / "theme.json"
        assert path.exists()
        data = load_json(path)
        assert data["code"] == "theme"
        assert data["data_type"] == "choices"
        assert "dark" in data["values"]

    def test_invoices_billing_organization_valid(self):
        """Verify billing organization JSON fixture defines suffix and sequence."""
        path = (
            SETUP_DIR / "invoices" / "dev_billing_organization" / "organizations.json"
        )
        assert path.exists()
        data = load_json(path)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["billing_suffix"] == "LS"
        assert data[0]["billing_start_sequence"] == 1001


@pytest.mark.django_db
class TestHostSeederExecution:
    """Validate discovery and execution of host project development seeders."""

    def test_auto_discover_finds_host_seeders(self):
        """Verify auto_discover_seeders imports all configured host seeders."""
        discovered = auto_discover_seeders()
        names = {mod.__name__ for mod in discovered}
        assert "setup.users.seeders" in names
        assert "setup.crm.seeder" in names
        assert "setup.invoices.seeder" in names

    def test_seeder_runner_persists_records(self):
        """Verify SeedDevelopmentData executes without errors and persists records."""
        instances = SeedDevelopmentData().run()
        assert len(instances) > 0

        User = get_user_model()
        Customer = get_customer_model()
        CustomerPhone = get_customer_phone_model()
        CustomerEmail = get_customer_email_model()
        CustomerAddress = get_customer_address_model()
        BillingOrg = get_billing_organization_model()

        assert User.objects.filter(username="driver_rajesh").exists()
        customer = Customer.objects.filter(
            first_name="Rajesh", last_name="Kumar"
        ).first()
        assert customer is not None
        assert CustomerPhone.objects.filter(
            customer=customer, phone="+919876543210"
        ).exists()
        assert CustomerEmail.objects.filter(
            customer=customer, email="rajesh@example.com"
        ).exists()
        assert CustomerAddress.objects.filter(customer=customer, city="Jaipur").exists()
        assert BillingOrg.objects.filter(billing_suffix="LS").exists()

    def test_customer_preferences_seeded(self):
        """Verify language and theme preferences are seeded for customers."""
        SeedDevelopmentData().run()

        Customer = get_customer_model()
        PreferenceType = get_customer_preference_type_model()
        Preference = get_customer_preference_model()

        assert PreferenceType.objects.filter(code="theme").exists()
        assert PreferenceType.objects.filter(code="language").exists()

        rajesh = Customer.objects.filter(first_name="Rajesh", last_name="Kumar").first()
        assert rajesh is not None
        assert Preference.objects.filter(
            customer=rajesh, preference_type__code="theme", value="dark"
        ).exists()
        assert Preference.objects.filter(
            customer=rajesh, preference_type__code="language", value="hi"
        ).exists()

        priya = Customer.objects.filter(first_name="Priya", last_name="Sharma").first()
        assert priya is not None
        assert Preference.objects.filter(
            customer=priya, preference_type__code="theme", value="light"
        ).exists()
        assert Preference.objects.filter(
            customer=priya, preference_type__code="language", value="en"
        ).exists()

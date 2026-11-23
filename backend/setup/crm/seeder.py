"""
Development seeders for CRM app in the host project.
"""

from __future__ import annotations

from core.setup.crm.seeder import (
    DevCustomerAddressSeeder,
    DevCustomerEmailSeeder,
    DevCustomerPhoneSeeder,
    DevCustomerSeeder,
)

__all__ = [
    "DevCustomerSeeder",
    "DevCustomerPhoneSeeder",
    "DevCustomerEmailSeeder",
    "DevCustomerAddressSeeder",
]

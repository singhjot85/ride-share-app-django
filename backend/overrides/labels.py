"""
labels.py: Localized UI copy and text labels for LoadShare / Routeway landing page.

NOTE: All labels have been migrated to the database Configuration table via
the production fixture at:
backend/setup/configurations/fixtures/configuration/users_template_label.json
and HostTemplateLabelFixtureSeeder.
"""

LANDING_PAGE_LABELS: dict[str, dict[str, str]] = {}

from core.config.settings.single_tenant import *  # noqa: F401

PROJECT_MIGRATION_PATH = "backend.db_migrations"
MIGRATION_MODULES = {
    app.rsplit(".", 1)[-1]: f'{PROJECT_MIGRATION_PATH}.{app.rsplit(".", 1)[-1]}'
    for app in PROJECT_APPS
}

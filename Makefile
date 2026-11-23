DEV_YAML_PATH = compose/local/compose.local.yml
PROJECT_NAME = rideshare
STACK_NAME = rideshare
PATH_TO_MANAGE = ./manage.py
TEST_DIR = tests
SCRIPTS_DIR = backend/core-common-django-apps/scripts
SUBMODULE_SKILLS_DIR = backend/core-common-django-apps/.agents
PARENT_SKILLS_DIR = .agents

# Database Tools Configurations (Overrideable at runtime)
PG_TOOLS_GRANULAR_COMPOSE ?= compose/local/backend/postgres/pg_tools_granular.yml
PG_TOOLS_VOLUME_COMPOSE ?= compose/local/backend/postgres/pg_tools.yml
DOCKER_NETWORK ?= $(PROJECT_NAME)_default
POSTGRES_CONTAINER ?= $(or $(STACK_NAME),rideshare)_postgres
VOLUME_NAME ?= $(or $(STACK_NAME),rideshare)_local_pg_data
BACKUP_FILE ?=
PG_DUMP_DIR ?=
PG_BACKUP_DIR ?=
# DB_NAME ?=  # Optional: specify single database name (e.g. make db-dump DB_NAME=rideshare_db)

include backend/core-common-django-apps/scripts/common.mk

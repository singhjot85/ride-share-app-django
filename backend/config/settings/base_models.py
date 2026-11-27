from core.config.settings.base_models import *

# Now swapping the app is just swapping this variable
# Build out you'r INSTALLED_APPS from this variable
USERS_APP = "apps.users"
AUTH_USER_MODEL = "users.User"

from django.conf import settings as django_settings
from datetime import timedelta

# Defaults are overridden by a dictionary JWT_SETTINGS in the Django server settings.py
DEFAULTS = {
    # Timedelta added to utcnow() to set the expiration time
    'EXPIRATION_DELTA': timedelta(seconds=86400),
    # Authorization header name. (e.g. `Authorization: Bearer JWT_TOKEN` )
    # Follows recommendations of [RFC6750](https://www.rfc-editor.org/rfc/rfc6750)
    'AUTH_HEADER': 'Bearer',
}


def get_jwt_settings():
    user_defined_settings = getattr(django_settings, 'JWT_SETTINGS', None)
    settings = DEFAULTS
    if user_defined_settings and isinstance(user_defined_settings, dict):
        for key, value in user_defined_settings.items():
            try:
                settings[key] = value
            except KeyError:
                continue
    return settings

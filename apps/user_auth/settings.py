from datetime import timedelta

# Defaults are overridden by a dictionary JWT_SETTINGS in the Django server settings.py
JWT_SETTINGS = {
    # Timedelta added to utcnow() to set the expiration time
    'EXPIRATION_DELTA': timedelta(seconds=86400),
    # Authorization header name. (e.g. `Authorization: Bearer JWT_TOKEN` )
    # Follows recommendations of [RFC6750](https://www.rfc-editor.org/rfc/rfc6750)
    'AUTH_HEADER': 'Bearer',
}

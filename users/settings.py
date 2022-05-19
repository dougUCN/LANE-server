from datetime import timedelta

GRAPHQL_JWT = {'JWT_VERIFY_EXPIRATION': True, 'JWT_EXPIRATION_DELTA': timedelta(days=1)}

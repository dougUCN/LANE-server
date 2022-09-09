import os
from django.conf import settings
from graphql import GraphQLResolveInfo

import jwt


class requires_auth(object):
    """
    Decorator for user authentication that examines the
    info.context argument for a starlette request

    Then checks the authorization header in the request object for authentication
    """

    def __init__(self, func):
        """Decorator initialization"""
        self.settings = getattr(settings, 'JWT_SETTINGS')
        self.func = func

    def __call__(self, *args, **kwargs):
        """
        The __call__ method is not called until the
        decorated function is called.
        """
        request_headers = self.get_request_headers(args)
        return self.func(*args, **kwargs)

    def get_request_headers(self, args):
        """
        Retrieves starlette request header from info object

        Returns a starlette header = immutable, case-insensitive, multi-dict
        """
        info = next(arg for arg in args if isinstance(arg, GraphQLResolveInfo))
        try:
            return info.context.get('request').get('headers')
        except AttributeError:
            return None

from graphql import GraphQLResolveInfo
from .settings import get_jwt_settings
import jwt


class requires_auth(object):
    """
    Decorator for user authentication that examines the
    info.context argument for a starlette request

    Then checks the authorization header in the request object for authentication
    """

    def __init__(self, func):
        """
        Decorator initialization
        Obtains settings from Django settings.py
        """
        self.settings = get_jwt_settings()
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


class AuthError(Exception):
    """Error Handler"""

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

"""
ASGI config for LANE_server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django

# Required to locate these up here before importing app-related things
# Otherwise daphne will not run properly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LANE_server.settings')
django.setup()

from django.core.asgi import get_asgi_application
from ariadne.asgi import GraphQL
from .graphql_config import schema
from django.urls import path, re_path
from django.conf import settings
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from starlette.middleware.cors import CORSMiddleware

application = AuthMiddlewareStack(
    URLRouter(
        [
            path(
                "graphql/",
                CORSMiddleware(
                    GraphQL(schema, debug=settings.DEBUG),
                    allow_origins=settings.CORS_ALLOWED_ORIGINS,
                    allow_methods=["*"],
                ),
            ),
            re_path(r"", get_asgi_application()),
        ]
    )
)

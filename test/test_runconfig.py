"""
Test queries and mutations related to histograms in the static db
"""

from LANE_server.asgi import application
from starlette.testclient import TestClient
import numpy as np
import datetime

from test.common import (
    GET_DEVICE,
    GET_DEVICES,
    GET_RUN_CONFIG,
    GET_RUN_CONFIGS,
    CREATE_DEVICE,
    DELETE_DEVICE,
    UPDATE_DEVICE,
    CREATE_RUN_CONFIG,
    DELETE_RUN_CONFIG,
    UPDATE_RUN_CONFIG,
    toSvgCoords,
)


class TestDevice:
    """
    Tests in this suite:

    """

    rng = np.random.default_rng()  # PRNG

    client = TestClient(application)  # starlette Test Client instance

    def post_to_test_client(self, query, variables):
        """
        Not a test

        Send an http request to the test client
        """
        response = self.client.post(
            "/graphql/",
            json={"query": query, "variables": variables},
        )
        if response.status_code != 200:
            raise Exception(f'Query failed to run by returning code of {response.status_code}')
        return response.json()


class TestRunConfig:
    """
    Tests in this suite:

    """

    rng = np.random.default_rng()  # PRNG

    client = TestClient(application)  # starlette Test Client instance

    def post_to_test_client(self, query, variables):
        """
        Not a test

        Send an http request to the test client
        """
        response = self.client.post(
            "/graphql/",
            json={"query": query, "variables": variables},
        )
        if response.status_code != 200:
            raise Exception(f'Query failed to run by returning code of {response.status_code}')
        return response.json()

"""
Test subscriptions
"""

from LANE_server.asgi import application
from starlette.testclient import TestClient
import numpy as np

from ariadne.asgi import (
    GQL_CONNECTION_ACK,
    GQL_CONNECTION_INIT,
    GQL_CONNECTION_TERMINATE,
    GQL_START,
    GQL_DATA,
    GQL_STOP,
    GQL_COMPLETE,
)

from test.common import (
    CREATE_HIST,
    DELETE_HIST,
    LIVE_HIST_SUBSCRIPTION,
    toSvgCoords,
)


class TestSubscription:
    """
    Tests in this suite:

    Connect via websocket via getHistograms()

    Validate lastRun string on subscription when no live histograms present

    Create liveHistograms, and validate content

    Update liveHistograms, and validate content

    Delete liveHistograms, and validate removal
    """

    ID = "subscription_test"
    NUM = 4  # number of fake histograms to create
    LENGTH = 50  # number of data points per hist
    LOW = 0  # min y range
    HIGH = 1000  # max y range
    histogram = {}  # Store generated test histograms to share among tests
    expected = {}  # Expected histogram to be returned when querying graphql
    X = {}  # Dictionary of np array data fed into histograms
    Y = {}  # Dictionary of np array data fed into histograms
    rng = np.random.default_rng()  # PRNG

    client = TestClient(application)  # Starlette test client

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

    def check_subscription_data_structure(self, data):
        """
        Not a test

        Expects subscription data to have the following structure
        {'getLiveHistograms': {'histograms': None, 'lastRun': str or None}}
        """
        if 'getLiveHistograms' not in list(data.keys()):
            raise Exception("list(data.keys()) is not ['getLiveHistograms']")
        elif 'histograms' not in list(data['getLiveHistograms'].keys()):
            raise Exception("'histograms' not in list(data['getLiveHistograms'].keys())")
        elif 'lastRun' not in list(data['getLiveHistograms'].keys()):
            raise Exception("'lastRun' not in list(data['getLiveHistograms'].keys())")
        elif data['getLiveHistograms']['lastRun'] and not isinstance(data['getLiveHistograms']['lastRun'], str):
            raise Exception("(data['getLiveHistograms']['lastRun'] and not isinstance(data['getLiveHistograms']['lastRun'], str))")
        elif data['getLiveHistograms']['histograms'] is not None:
            raise Exception("data['getLiveHistograms']['histograms'] is not None")

        return True

    def compare_histograms(self, expected, received):
        """
        Not a test

        Checks if the values of keys in `expected` match those of `received`
        returns: true if histograms match
        """
        for key, expectedValue in expected.items():
            if received[key] != expectedValue:
                print(f'Mismatch for key "{key}"')
                return False
        return True

    def test_websocket_connection(self):
        """
        Validate if connection to the graphql endpoint via websocket works
        """
        with self.client.websocket_connect("/graphql/", "graphql-ws") as ws:
            ws.send_json({"type": GQL_CONNECTION_INIT})
            ws.send_json(
                {
                    "type": GQL_START,
                    "id": self.ID,
                    "payload": {"query": LIVE_HIST_SUBSCRIPTION},
                }
            )
            response = ws.receive_json()
            assert response["type"] == GQL_CONNECTION_ACK
            response = ws.receive_json()
            assert response["type"] == GQL_DATA
            assert response["id"] == self.ID

            assert self.check_subscription_data_structure(response["payload"]["data"])

            ws.send_json({"type": GQL_STOP, "id": self.ID})
            response = ws.receive_json()
            assert response["type"] == GQL_COMPLETE
            ws.send_json({"type": GQL_CONNECTION_TERMINATE})

    def test_add_live_histograms_content(self):
        """
        Creates live histograms. Validate that subscription returns the expected content
        """
        # Create histograms in live db
        startID = 0
        ids = np.arange(startID, startID + self.NUM).tolist()
        successfulHistCreation = []
        for new_id in ids:
            self.X[new_id] = np.arange(self.LENGTH)
            self.Y[new_id] = self.rng.integers(low=self.LOW, high=self.HIGH, size=self.LENGTH)

            # Histogram params to pass to mutation
            self.histogram[new_id] = {
                'id': new_id,
                'data': toSvgCoords(self.X[new_id].tolist(), self.Y[new_id].tolist()),
                'xrange': {'min': float(self.X[new_id][0]), 'max': float(self.X[new_id][-1])},
                'yrange': {'min': self.LOW, 'max': self.HIGH},
                'name': f'unit_test_name',
                'type': f'unit_test_type{new_id}',
                'isLive': True,
            }
            # Histogram expected to recieve back for later queries
            # Note that we expect `id` to be a string
            # New fields `len` and `current`
            # Also `isLive` is not returned
            self.expected[new_id] = self.histogram[new_id].copy()
            self.expected[new_id]['id'] = str(new_id)
            self.expected[new_id]['len'] = self.LENGTH
            self.expected[new_id]['current'] = self.expected[new_id]['data'][-1]
            self.expected[new_id].pop('isLive')

            # Create histograms
            response = self.post_to_test_client(
                query=CREATE_HIST,
                variables={"hist": self.histogram[new_id]},
            )
            successfulHistCreation.append(response['data']['createHistogram']['success'])
        assert all(successfulHistCreation)

        # Open websocket
        with self.client.websocket_connect("/graphql/", "graphql-ws") as ws:
            ws.send_json({"type": GQL_CONNECTION_INIT})
            ws.send_json(
                {
                    "type": GQL_START,
                    "id": self.ID,
                    "payload": {"query": LIVE_HIST_SUBSCRIPTION},
                }
            )
            response = ws.receive_json()
            assert response["type"] == GQL_CONNECTION_ACK
            response = ws.receive_json()
            assert response["type"] == GQL_DATA
            assert response["id"] == self.ID

            histograms = response["payload"]["data"]['getLiveHistograms']['histograms']

            ws.send_json({"type": GQL_STOP, "id": self.ID})
            response = ws.receive_json()
            assert response["type"] == GQL_COMPLETE
            ws.send_json({"type": GQL_CONNECTION_TERMINATE})

        # Check histogram data matches expected
        histsMatch = []
        for histogram in histograms:
            id = int(histogram['id'])
            histsMatch.append(self.compare_histograms(self.expected[id], histogram))

        assert len(histograms) == self.NUM and all(histsMatch)

    def test_delete_live_histograms_content(self):
        """
        Delete live histograms. Validate that subscription returns the expected content
        """
        successFlag = []
        for id in self.histogram.keys():
            # Delete histogram
            response = self.post_to_test_client(
                query=DELETE_HIST,
                variables={"id": id, "isLive": True},
            )
            successFlag.append(response['data']['deleteHistogram']['success'])

        assert all(successFlag)

        with self.client.websocket_connect("/graphql/", "graphql-ws") as ws:
            ws.send_json({"type": GQL_CONNECTION_INIT})
            ws.send_json(
                {
                    "type": GQL_START,
                    "id": self.ID,
                    "payload": {"query": LIVE_HIST_SUBSCRIPTION},
                }
            )
            response = ws.receive_json()
            assert response["type"] == GQL_CONNECTION_ACK
            response = ws.receive_json()
            assert response["type"] == GQL_DATA
            assert response["id"] == self.ID

            assert self.check_subscription_data_structure(response["payload"]["data"])

            ws.send_json({"type": GQL_STOP, "id": self.ID})
            response = ws.receive_json()
            assert response["type"] == GQL_COMPLETE
            ws.send_json({"type": GQL_CONNECTION_TERMINATE})

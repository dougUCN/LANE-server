"""
Test subscriptions
"""

from LANE_server.asgi import application
from starlette.testclient import TestClient

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
    LIVE_HIST_SUBSCRIPTION,
    toSvgCoords,
)


class TestSubscription:
    """
    # Tests in this suite

    Connect via websocket via getHistograms()

    Validate lastRun string on subscription when no live histograms present

    Create liveHistograms, and validate content

    Update liveHistograms, and validate content

    Delete liveHistograms, and validate removal
    """

    ID = "subscription_test"

    def test_websocket_connection(self):
        """
        Validate if connection to the graphql endpoint via websocket works
        """
        client = TestClient(application)

        with client.websocket_connect("/graphql/", "graphql-ws") as ws:
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
            ws.send_json({"type": GQL_STOP, "id": self.ID})
            response = ws.receive_json()
            assert response["type"] == GQL_COMPLETE
            ws.send_json({"type": GQL_CONNECTION_TERMINATE})

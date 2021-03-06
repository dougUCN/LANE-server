"""
Test queries and mutations related to histograms in the static db
"""

from LANE_server.asgi import application
from starlette.testclient import TestClient
import numpy as np
import datetime

from test.common import (
    GET_HIST_IDS,
    CREATE_HIST,
    GET_HISTOGRAM,
    GET_HISTOGRAMS,
    UPDATE_HIST,
    DELETE_HIST,
    toSvgCoords,
)


class TestStaticHistogram:
    """
    Tests in this suite:

    Create histograms in static db, check that the data is correct

    Update histograms in the static db, check that the data is correct

    Check getHistogram and getHistograms queries on created histograms

    Remove created histograms from static db, check for removal
    """

    NUM = 4  # number of fake histograms to create
    LENGTH = 50  # number of data points per hist
    LOW = 0  # min y range
    HIGH = 1000  # max y range
    histogram = {}  # Store generated test histograms to share among tests
    expected = {}  # Expected histogram to be returned when querying graphql
    X = {}  # Dictionary of np array data fed into histograms
    Y = {}  # Dictionary of np array data fed into histograms
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

    def make_histogram_list(self, data):
        """
        Not a test
        """
        histogramList = []
        for datum in data:
            histogramList.append(int(datum['id']))
        return histogramList

    def test_create_histograms(self):
        """
        Create histograms in the database
        """
        # Get existing histograms in db
        response = self.post_to_test_client(
            query=GET_HIST_IDS,
            variables={"isLive": False},
        )
        data = response["data"]["getHistograms"]
        histogramList = self.make_histogram_list(data)

        if histogramList:
            startID = np.amax(histogramList) + 1
        else:
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
                'isLive': False,
            }
            # Histogram expected to recieve back for later queries
            # Note that we expect `id` to be a string, and there is a new `len` field
            # Also `isLive` is not returned
            self.expected[new_id] = self.histogram[new_id].copy()
            self.expected[new_id]['id'] = str(new_id)
            self.expected[new_id]['len'] = self.LENGTH
            self.expected[new_id].pop('isLive')

            # Create histograms
            response = self.post_to_test_client(
                query=CREATE_HIST,
                variables={"hist": self.histogram[new_id]},
            )
            successfulHistCreation.append(response['data']['createHistogram']['success'])
        assert all(successfulHistCreation)

    def test_get_histogram(self):
        """
        Get histograms by ID via getHistogram()
        Check if data of histogram created in the db matches the expected output
        """

        histsMatch = []
        for id in self.histogram.keys():
            response = self.post_to_test_client(
                query=GET_HISTOGRAM,
                variables={"id": int(id)},
            )
            histogram = response['data']['getHistogram']
            histsMatch.append(self.compare_histograms(self.expected[id], histogram))
        assert all(histsMatch)

    def test_get_histograms(self):
        """
        Gets histograms by ID via getHistograms()
        """
        response = self.post_to_test_client(
            query=GET_HISTOGRAMS,
            variables={"ids": list(self.histogram.keys())},
        )
        histograms = response['data']['getHistograms']

        histsMatch = []
        for histogram in histograms:
            id = int(histogram['id'])
            histsMatch.append(self.compare_histograms(self.expected[id], histogram))

        assert len(histograms) == self.NUM and all(histsMatch)

    def test_get_histograms_filters(self):
        """
        Check if date filter for getHistograms() works
        Check if Names filters work
        Check if Types filters work
        """

        # get date when first histogram was created for this test
        firstID = next(iter(self.histogram))
        response = self.post_to_test_client(
            query=GET_HISTOGRAM,
            variables={"id": firstID},
        )
        firstCreated = response['data']['getHistogram']['created']

        # Get histograms created during this test
        response = self.post_to_test_client(
            query=GET_HIST_IDS,
            variables={
                "minDate": firstCreated,
                "maxDate": datetime.datetime.utcnow().isoformat(),
                "isLive": False,
            },
        )

        data = response["data"]["getHistograms"]
        createdDuringTest = self.make_histogram_list(data)

        assert len(createdDuringTest) == self.NUM

        # Get histograms created after this test (should be none)
        response = self.post_to_test_client(
            query=GET_HIST_IDS,
            variables={
                "minDate": datetime.datetime.utcnow().isoformat(),
                "isLive": False,
            },
        )
        data = response["data"]["getHistograms"]
        createdAfterNow = self.make_histogram_list(data)
        assert createdAfterNow == []

        # Filter histograms by giving a list of names
        response = self.post_to_test_client(
            query=GET_HIST_IDS,
            variables={
                "names": [x['name'] for _, x in self.expected.items()],
                "isLive": False,
            },
        )
        data = response["data"]["getHistograms"]
        nameFilter = self.make_histogram_list(data)

        assert len(nameFilter) == self.NUM

        # Filter histograms by giving a list of types
        response = self.post_to_test_client(
            query=GET_HIST_IDS,
            variables={
                "types": [x['type'] for _, x in self.expected.items()],
                "isLive": False,
            },
        )
        data = response["data"]["getHistograms"]
        typeFilter = self.make_histogram_list(data)

        assert len(typeFilter) >= 4

    def test_update_histogram(self):
        """
        Update histograms and check if content is as expected
        """
        client = TestClient(application)

        # Update histograms with new data
        successFlag = []
        updateParams = {}
        for id in self.histogram.keys():
            self.X[id] = np.arange(self.LENGTH)
            self.Y[id] = self.rng.integers(low=self.LOW, high=self.HIGH, size=self.LENGTH)
            updateParams[id] = {
                'id': id,
                'data': toSvgCoords(self.X[id].tolist(), self.Y[id].tolist()),
            }
            response = self.post_to_test_client(
                query=UPDATE_HIST,
                variables={"hist": updateParams[id]},
            )
            successFlag.append(response['data']['updateHistogram']['success'])
        assert all(successFlag)

        # Get histograms by ids to validate the update
        response = self.post_to_test_client(
            query=GET_HISTOGRAMS,
            variables={"ids": list(self.histogram.keys())},
        )
        histograms = response['data']['getHistograms']

        assert len(histograms) == self.NUM

        histsMatchExpected = []
        for histogram in histograms:
            id = int(histogram['id'])

            # Without updating expected value, histograms should not match
            histsMatchExpected.append(not self.compare_histograms(self.expected[id], histogram))

            # Now the histograms should match
            self.expected[id]['data'] = toSvgCoords(self.X[id], self.Y[id])
            histsMatchExpected.append(self.compare_histograms(self.expected[id], histogram))

        assert all(histsMatchExpected)

    def test_delete_histogram(self):
        """
        Delete histograms and confirm removal from the db
        """

        successFlag = []
        confirmedRemoval = []
        for id in self.histogram.keys():
            # Delete histogram
            response = self.post_to_test_client(
                query=DELETE_HIST,
                variables={"id": id, "isLive": False},
            )
            successFlag.append(response['data']['deleteHistogram']['success'])

            # Validate removal from the db
            response = self.post_to_test_client(
                query=GET_HIST_IDS,
                variables={"isLive": False},
            )
            data = response["data"]["getHistograms"]
            histogramList = self.make_histogram_list(data)

            confirmedRemoval.append(id not in histogramList)

        assert all(successFlag) and all(confirmedRemoval)

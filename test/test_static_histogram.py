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
    # Tests in this suite

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

    def check_response(self, status_code):
        """Raise an error upon a bad response code"""
        if status_code != 200:
            raise Exception(f'Query failed to run by returning code of {status_code}')

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
        histogramList = []
        for datum in data:
            histogramList.append(int(datum['id']))
        return histogramList

    def test_create_histograms(self):
        """
        Create histograms in the database
        """
        client = TestClient(application)

        response = client.post(
            "/graphql/",
            json={"query": GET_HIST_IDS, "variables": {"isLive": False}},
        )
        self.check_response(response.status_code)
        data = response.json()["data"]["getHistograms"]
        histogramList = self.make_histogram_list(data)

        if histogramList:
            startID = np.amax(histogramList) + 1
        else:
            startID = 0
        ids = np.arange(startID, startID + self.NUM).tolist()

        successFlag = []
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
            response = client.post(
                "/graphql/",
                json={
                    "query": CREATE_HIST,
                    "variables": {"hist": self.histogram[new_id]},
                },
            )
            self.check_response(response.status_code)
            successFlag.append(response.json()['data']['createHistogram']['success'])
        assert all(successFlag)

    def test_get_histogram(self):
        """
        Get histograms by ID via getHistogram()
        Check if data of histogram created in the db matches the expected output
        """
        client = TestClient(application)

        histsMatch = []
        for id in self.histogram.keys():
            response = client.post(
                "/graphql/",
                json={
                    "query": GET_HISTOGRAM,
                    "variables": {"id": int(id)},
                },
            )
            self.check_response(response.status_code)
            histogram = response.json()['data']['getHistogram']
            histsMatch.append(self.compare_histograms(self.expected[id], histogram))
        assert all(histsMatch)

    def test_get_histograms(self):
        """
        Gets histograms by ID via getHistograms()
        """
        client = TestClient(application)

        response = client.post(
            "/graphql/",
            json={
                "query": GET_HISTOGRAMS,
                "variables": {"ids": list(self.histogram.keys())},
            },
        )
        self.check_response(response.status_code)
        histograms = response.json()['data']['getHistograms']

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
        client = TestClient(application)

        # get date when first histogram was created for this test
        firstID = next(iter(self.histogram))
        response = client.post(
            "/graphql/",
            json={
                "query": GET_HISTOGRAM,
                "variables": {"id": firstID},
            },
        )
        self.check_response(response.status_code)
        firstCreated = response.json()['data']['getHistogram']['created']

        # Get histograms created during this test
        response = client.post(
            "/graphql/",
            json={
                "query": GET_HIST_IDS,
                "variables": {
                    "minDate": firstCreated,
                    "maxDate": datetime.datetime.utcnow().isoformat(),
                    "isLive": False,
                },
            },
        )
        self.check_response(response.status_code)
        data = response.json()["data"]["getHistograms"]
        createdDuringTest = self.make_histogram_list(data)

        assert len(createdDuringTest) == self.NUM

        # Get histograms created after this test (should be none)
        response = client.post(
            "/graphql/",
            json={
                "query": GET_HIST_IDS,
                "variables": {
                    "minDate": datetime.datetime.utcnow().isoformat(),
                    "isLive": False,
                },
            },
        )
        self.check_response(response.status_code)
        data = response.json()["data"]["getHistograms"]
        createdAfterNow = self.make_histogram_list(data)

        assert createdAfterNow == []

        # Filter histograms by giving a list of names
        response = client.post(
            "/graphql/",
            json={
                "query": GET_HIST_IDS,
                "variables": {
                    "names": [x['name'] for _, x in self.expected.items()],
                    "isLive": False,
                },
            },
        )
        self.check_response(response.status_code)
        data = response.json()["data"]["getHistograms"]
        nameFilter = self.make_histogram_list(data)

        assert len(nameFilter) == self.NUM

        # Filter histograms by giving a list of types
        response = client.post(
            "/graphql/",
            json={
                "query": GET_HIST_IDS,
                "variables": {
                    "types": [x['type'] for _, x in self.expected.items()],
                    "isLive": False,
                },
            },
        )
        self.check_response(response.status_code)
        data = response.json()["data"]["getHistograms"]
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
            response = client.post(
                "/graphql/",
                json={
                    "query": UPDATE_HIST,
                    "variables": {"hist": updateParams[id]},
                },
            )
            self.check_response(response.status_code)
            successFlag.append(response.json()['data']['updateHistogram']['success'])
        assert all(successFlag)

        # Get histograms by ids to validate the update
        response = client.post(
            "/graphql/",
            json={
                "query": GET_HISTOGRAMS,
                "variables": {"ids": list(self.histogram.keys())},
            },
        )
        self.check_response(response.status_code)
        histograms = response.json()['data']['getHistograms']

        assert len(histograms) == self.NUM

        histsMatch = []
        for histogram in histograms:
            id = int(histogram['id'])

            # Without updating expected value, histograms should not match
            histsMatch.append(not self.compare_histograms(self.expected[id], histogram))

            # Now the histograms should match
            self.expected[id]['data'] = toSvgCoords(self.X[id], self.Y[id])
            histsMatch.append(self.compare_histograms(self.expected[id], histogram))

        assert all(histsMatch)

    def test_delete_histogram(self):
        """
        Delete histograms and confirm removal from the db
        """
        client = TestClient(application)

        successFlag = []
        confirmedRemoval = []
        for id in self.histogram.keys():
            # Delete histogram
            response = client.post(
                "/graphql/",
                json={
                    "query": DELETE_HIST,
                    "variables": {"id": id, "isLive": False},
                },
            )
            self.check_response(response.status_code)
            successFlag.append(response.json()['data']['deleteHistogram']['success'])

            # Validate removal from the db
            response = client.post(
                "/graphql/",
                json={
                    "query": GET_HIST_IDS,
                    "variables": {"isLive": False},
                },
            )
            self.check_response(response.status_code)
            data = response.json()["data"]["getHistograms"]
            histogramList = self.make_histogram_list(data)

            confirmedRemoval.append(id not in histogramList)

        assert all(successFlag) and all(confirmedRemoval)

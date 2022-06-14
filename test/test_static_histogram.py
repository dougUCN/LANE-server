"""
Unit tests for the BE related to static histograms

Note that Pytest requires the filename and test functions to start with `test_*`
"""

from LANE_server.asgi import application
from starlette.testclient import TestClient
import numpy as np
import datetime


class TestStaticHistogram:
    """
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

    def test_create_histograms(self):
        """
        Create histograms in the database
        """
        client = TestClient(application)

        histogramList = gqlc.listHistograms(isLive=False)
        if histogramList:
            startID = np.amax(histogramList) + 1
        else:
            startID = 0
        ids = np.arange(startID, startID + self.NUM)

        successFlag = []
        for new_id in ids:
            self.X[new_id] = np.arange(self.LENGTH)
            self.Y[new_id] = self.rng.integers(low=self.LOW, high=self.HIGH, size=self.LENGTH)

            # Histogram params to pass to mutation
            self.histogram[new_id] = {
                'id': new_id,
                'data': gqlc.toSvgStr(self.X[new_id], self.Y[new_id]),
                'xrange': {'min': self.X[new_id][0], 'max': self.X[new_id][-1]},
                'yrange': {'min': self.LOW, 'max': self.HIGH},
                'name': f'unit_test_name',
                'type': f'unit_test_type{new_id}',
                'isLive': False,
            }
            # Histgoram expected to recieve back for later queries
            self.expected[new_id] = self.histogram[new_id].copy()
            self.expected[new_id]['id'] = str(new_id)
            self.expected[new_id]['data'] = gqlc.toSvgCoords(self.X[new_id], self.Y[new_id])
            self.expected[new_id]['len'] = self.LENGTH
            self.expected[new_id].pop('isLive')

            successFlag.append(gqlc.createHistogram(**self.histogram[new_id])['data']['createHistogram']['success'])
        assert all(successFlag)

    def test_get_histogram(self):
        """
        Get histograms by ID via getHistogram()
        Check if data of histogram created in the db matches the expected output
        """
        client = TestClient(application)

        histsMatch = []
        for id in self.histogram.keys():
            histogram = gqlc.getHistogram(id=id)['data']['getHistogram']
            histsMatch.append(self.compare_histograms(self.expected[id], histogram))
        assert all(histsMatch)

    def test_get_histograms(self):
        """
        Gets histograms by ID via getHistograms()
        """
        client = TestClient(application)

        histograms = gqlc.getHistograms(ids=list(self.histogram.keys()))['data']['getHistograms']

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

        # get date when first histogram created for this test
        firstID = next(iter(self.histogram))
        firstCreated = gqlc.getHistogram(id=firstID)['data']['getHistogram']['created']

        # Apply filters to histograms
        createdDuringTest = gqlc.listHistograms(minDate=firstCreated, maxDate=datetime.datetime.utcnow(), isLive=False)
        createdAfterNow = gqlc.listHistograms(minDate=datetime.datetime.utcnow(), isLive=False)
        nameFilter = gqlc.listHistograms(names=[x['name'] for _, x in self.expected.items()])
        typeFilter = gqlc.listHistograms(types=[x['type'] for _, x in self.expected.items()])

        assert len(createdDuringTest) == self.NUM and createdAfterNow == [] and len(nameFilter) == self.NUM and len(typeFilter) >= 4

    def test_update_histogram(self):
        """
        Update histograms and check if content is as expected
        """
        client = TestClient(application)

        successFlag = []
        updateParams = {}
        for id in self.histogram.keys():
            self.X[id] = np.arange(self.LENGTH)
            self.Y[id] = self.rng.integers(low=self.LOW, high=self.HIGH, size=self.LENGTH)
            updateParams[id] = {
                'id': id,
                'data': gqlc.toSvgStr(self.X[id], self.Y[id]),
            }
            successFlag.append(gqlc.updateHistogram(**updateParams[id])['data']['updateHistogram']['success'])

        histograms = gqlc.getHistograms(ids=list(self.histogram.keys()))['data']['getHistograms']

        histsMatch = []
        for histogram in histograms:
            id = int(histogram['id'])

            # Without updating expected value, histograms should not match
            histsMatch.append(not self.compare_histograms(self.expected[id], histogram))

            # Now the histograms should match
            self.expected[id]['data'] = gqlc.toSvgCoords(self.X[id], self.Y[id])
            histsMatch.append(self.compare_histograms(self.expected[id], histogram))

        assert len(histograms) == self.NUM and all(histsMatch) and all(successFlag)

    def test_delete_histogram(self):
        """
        Delete histograms and confirm removal from the db
        """
        client = TestClient(application)

        successFlag = []
        confirmedRemoval = []
        for id in self.histogram.keys():
            successFlag.append(gqlc.deleteHistogram(id=id)['data']['deleteHistogram']['success'])
            confirmedRemoval.append(id not in gqlc.listHistograms(isLive=False))

        assert all(successFlag) and all(confirmedRemoval)

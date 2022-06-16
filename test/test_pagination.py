"""
Test pagination of getHistTableEntries
"""

from LANE_server.asgi import application
from starlette.testclient import TestClient
import numpy as np
from test.common import (
    GET_HIST_TABLE,
    CREATE_HIST,
    DELETE_HIST,
    toSvgCoords,
)


class TestHistTable:
    """
    # Tests in this suite

    Create histograms and verify that the histogram table gets updated correctly

    Paginate through the created histogram table and validate that the query returns expected values

    Delete histograms and verify that the histogram table updates correctly
    """

    NUM = 10  # number of runs to create
    LENGTH = 50  # Size of each histogram
    LOW = 0  # Min y range of histogram
    HIGH = 1000  # Max y range of histogram
    PER_RUN = 4  # Number of histograms to make per run
    PER_PAGE = 4  # How many table entries to fetch per page in the check
    rng = np.random.default_rng()
    expected = {}

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

    def test_create_hist_table_entries(self):
        """
        Tests creation of histogram table entries
        """

        # Query for the latest entry in HistTable, if any
        data = self.post_to_test_client(query=GET_HIST_TABLE, variables={"first": 1})['data']['getHistTableEntries']

        runHeader = "run"

        # Get first unoccupied run index and hist id
        if not data['edges']:
            hist_offset = 0
            run_offset = 0
        else:
            hist_offset = np.amax([int(id) for id in data['edges'][0]['node']['histIDs']]) + 1

            if runHeader in data['edges'][0]['node']['name']:
                run_offset = int(data['edges'][0]['node']['name'].split(runHeader)[1]) + 1
            else:
                run_offset = 0

        # Create a few histograms
        hist_id = hist_offset
        x = np.arange(self.LENGTH)
        histogramCreationSuccessful = []
        for run_id in np.arange(run_offset, run_offset + self.NUM):
            runname = f'{runHeader}{run_id}'
            temp_id = []
            for type_id in np.arange(self.PER_RUN):
                y = self.rng.integers(low=self.LOW, high=self.HIGH, size=self.LENGTH)
                params = {
                    'id': int(hist_id),
                    'data': toSvgCoords(x.tolist(), y.tolist()),
                    'xrange': {'min': float(x[0]), 'max': float(x[-1])},
                    'yrange': {'min': self.LOW, 'max': self.HIGH},
                    'name': runname,
                    'type': f'detector_type_{type_id}',
                    'isLive': False,
                }

                response = self.post_to_test_client(query=CREATE_HIST, variables={"hist": params})
                histogramCreationSuccessful.append(response['data']['createHistogram']['success'])

                temp_id.append(hist_id)
                hist_id += 1

            self.expected[runname] = sorted(temp_id)  # Save for checking in later tests
        assert all(histogramCreationSuccessful)

        # Get all created histograms
        data = self.post_to_test_client(query=GET_HIST_TABLE, variables={"first": self.NUM})['data']['getHistTableEntries']

        # Check that the response is expected
        tableEntryMatchesExpected = []
        for edge in data['edges']:
            table_ids = sorted([int(id) for id in edge['node']['histIDs']])
            tableEntryMatchesExpected.append(self.expected[edge['node']['name']] == table_ids)
        assert all(tableEntryMatchesExpected)

    def test_paginate_hist_table_entries(self):
        """
        Get pages of hist table, verifying entries until complete
        Since table is sorted in descending order of creation date,
        this should match the `self.expect` values inverted
        """
        tableEntryMatchesExpected = []
        expected_hist_ids = list(self.expected.values())[::-1]
        hasNextPage = True
        index = 0
        currentPage = 0
        variables = {"first": self.PER_PAGE}

        while hasNextPage:
            data = self.post_to_test_client(query=GET_HIST_TABLE, variables=variables)['data']['getHistTableEntries']

            variables['after'] = data['pageInfo']['endCursor']
            hasNextPage = data['pageInfo']['hasNextPage']

            for edge in data['edges']:
                table_ids = sorted([int(id) for id in edge['node']['histIDs']])
                tableEntryMatchesExpected.append(expected_hist_ids[index] == table_ids)
                index += 1
                if index >= len(expected_hist_ids):
                    hasNextPage = False
                    break
            currentPage += 1

        assert all(tableEntryMatchesExpected)

    def test_delete_hist_table_entries(self):
        """
        Verify that deleting histograms also removes them from the hist table
        """
        successfullyRemovedFromTable = []
        successfulHistDeletion = []
        correctRunOrder = []

        for key, value in zip(list(self.expected.keys())[::-1], list(self.expected.values())[::-1]):
            for id in value:
                # Delete runs one by one
                response = self.post_to_test_client(query=DELETE_HIST, variables={"id": int(id)})
                successfulHistDeletion.append(response['data']['deleteHistogram']['success'])

                # When the histIDs list is empty on the table entry, the table entry should be deleted
                if id is value[-1]:
                    continue

                # Get last created entry
                response = self.post_to_test_client(query=GET_HIST_TABLE, variables={"first": 1})
                data = response['data']['getHistTableEntries']

                correctRunOrder.append(data['edges'][0]['node']['name'] == key)
                successfullyRemovedFromTable.append(data['edges'][0]['node']['name'] == value.copy().remove(id))

        assert successfullyRemovedFromTable and successfulHistDeletion and correctRunOrder

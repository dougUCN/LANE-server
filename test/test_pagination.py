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

    def check_response(self, status_code):
        """Raise an error upon a bad response code"""
        if status_code != 200:
            raise Exception(f'Query failed to run by returning code of {status_code}')

    def test_create_hist_table_entries(self):
        """
        Tests creation of histogram table entries
        """
        client = TestClient(application)

        # Query for the latest entry in HistTable, if any
        response = client.post(
            "/graphql/",
            json={"query": GET_HIST_TABLE, "variables": {"first": 1}},
        )
        self.check_response(response.status_code)
        data = response.json()['data']['getHistTableEntries']

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
                response = client.post(
                    "/graphql/",
                    json={
                        "query": CREATE_HIST,
                        "variables": {"hist": params},
                    },
                )
                self.check_response(response.status_code)
                temp_id.append(hist_id)
                hist_id += 1

            self.expected[runname] = sorted(temp_id)  # Save for checking in later tests

        # Get all created histograms
        response = client.post(
            "/graphql/",
            json={"query": GET_HIST_TABLE, "variables": {"first": self.NUM}},
        )
        self.check_response(response.status_code)
        data = response.json()['data']['getHistTableEntries']

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
        client = TestClient(application)

        tableEntryMatchesExpected = []
        expected_hist_ids = list(self.expected.values())[::-1]
        hasNextPage = True
        index = 0
        currentPage = 0
        variables = {"first": self.PER_PAGE}

        while hasNextPage:
            response = client.post(
                "/graphql/",
                json={"query": GET_HIST_TABLE, "variables": variables},
            )
            self.check_response(response.status_code)
            data = response.json()['data']['getHistTableEntries']

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
        client = TestClient(application)

        successfullyRemovedFromTable = []
        successfulHistDeletion = []
        correctRunOrder = []

        for key, value in zip(list(self.expected.keys())[::-1], list(self.expected.values())[::-1]):
            for id in value:
                # Delete runs one by one
                response = client.post(
                    "/graphql/",
                    json={"query": DELETE_HIST, "variables": {"id": int(id)}},
                )
                self.check_response(response.status_code)

                successfulHistDeletion.append(response.json()['data']['deleteHistogram']['success'])

                # When the histIDs list is empty on the table entry, the table entry should be deleted
                if id is value[-1]:
                    continue

                # Get last created entry
                response = client.post(
                    "/graphql/",
                    json={"query": GET_HIST_TABLE, "variables": {"first": 1}},
                )
                self.check_response(response.status_code)
                data = response.json()['data']['getHistTableEntries']

                correctRunOrder.append(data['edges'][0]['node']['name'] == key)
                successfullyRemovedFromTable.append(data['edges'][0]['node']['name'] == value.copy().remove(id))

        assert successfullyRemovedFromTable and successfulHistDeletion and correctRunOrder

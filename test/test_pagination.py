"""
Test pagination of getHistTableEntries
"""

import gqlComms as gqlc
import numpy as np


class TestHistTable:
    NUM = 10  # number of runs to create
    LENGTH = 50  # Size of each histogram
    LOW = 0  # Min y range of histogram
    HIGH = 1000  # Max y range of histogram
    PER_RUN = 4  # Number of histograms to make per run
    PER_PAGE = 4  # How many table entries to fetch per page in the check
    rng = np.random.default_rng()
    expected = {}

    def test_createHistTableEntries(self):
        """
        Tests creation of histogram table entries
        """
        runHeader = "run"

        # Get first unoccupied run index and hist id
        data = gqlc.getHistTable(first=1)['data']['getHistTableEntries']
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
                    'id': hist_id,
                    'data': gqlc.toSvgStr(x, y),
                    'xrange': {'min': x[0], 'max': x[-1]},
                    'yrange': {'min': self.LOW, 'max': self.HIGH},
                    'name': runname,
                    'type': f'detector_type_{type_id}',
                    'isLive': False,
                }
                gqlc.createHistogram(**params)
                temp_id.append(hist_id)
                hist_id += 1

            self.expected[runname] = sorted(temp_id)  # Save for checking in later tests

        # Get all created histograms
        data = gqlc.getHistTable(first=self.NUM)['data']['getHistTableEntries']

        # Check that the response is expected
        tableEntryMatchesExpected = []
        for edge in data['edges']:
            table_ids = sorted([int(id) for id in edge['node']['histIDs']])
            tableEntryMatchesExpected.append(self.expected[edge['node']['name']] == table_ids)
        assert all(tableEntryMatchesExpected)

    def test_paginateHistTableEntries(self):
        """
        Get pages of hist table, verifying entries until complete
        Since table is sorted in descending order of creation date,
        this should match the `self.expect` values inverted
        """

        tableEntryMatchesExpected = []
        expected_hist_ids = list(self.expected.values())[::-1]
        hasNextPage = True
        cursor = None
        index = 0
        currentPage = 0

        while hasNextPage:
            data = gqlc.getHistTable(first=self.PER_PAGE, after=cursor)['data']['getHistTableEntries']
            cursor = data['pageInfo']['endCursor']
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

    def test_deleteHistTableEntries(self):
        """Verify that deleting histograms also removes them from the hist table"""
        successfullyRemovedFromTable = []
        successfulHistDeletion = []
        correctRunOrder = []

        for key, value in zip(list(self.expected.keys())[::-1], list(self.expected.values())[::-1]):
            for id in value:
                # Delete runs one by one
                successfulHistDeletion.append(gqlc.deleteHistogram(id=id)['data']['deleteHistogram']['success'])

                # When the histIDs list is empty on the table entry, the table entry should be deleted
                if id is value[-1]:
                    continue

                # Get last created entry
                data = gqlc.getHistTable(first=1)['data']['getHistTableEntries']
                correctRunOrder.append(data['edges'][0]['node']['name'] == key)
                successfullyRemovedFromTable.append(data['edges'][0]['node']['name'] == value.copy().remove(id))

        assert successfullyRemovedFromTable and successfulHistDeletion and correctRunOrder

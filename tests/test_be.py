"""
Unit tests for the BE

Assuming the BE server is running, queries the graphql endpoint

Note that Pytest requires the filename and test functions to start with `test_*`
"""

from gqlComms import listHistograms


def test_listHistograms():
    _, response = listHistograms(isLive=False)
    assert response

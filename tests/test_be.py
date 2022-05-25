"""
Unit tests for the BE

Assuming the BE server is running, queries the graphql endpoint

Note that Pytest requires the filename and test functions to start with `test_*`
"""


def listHistograms():
    _, response = listHistograms(isLive=False)
    assert response

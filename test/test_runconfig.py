"""
Test queries and mutations related to histograms in the static db
"""

from LANE_server.asgi import application
from starlette.testclient import TestClient
import numpy as np
import datetime

from test.common import (
    GET_DEVICE,
    GET_DEVICES,
    GET_RUN_CONFIG,
    GET_RUN_CONFIGS,
    CREATE_DEVICE,
    DELETE_DEVICE,
    UPDATE_DEVICE,
    CREATE_RUN_CONFIG,
    DELETE_RUN_CONFIG,
    UPDATE_RUN_CONFIG,
    toSvgCoords,
)


class TestDevice:
    """
    Tests in this suite:

    Create a device and validate its contents with GetDevice()

    Test the GetDevices() query

    Update a device and validate its contents

    Delete a device and validate its deletion

    """

    client = TestClient(application)  # starlette Test Client instance

    deviceNames = ["test_device0", "test_device1"]  # Names of the fake devices to create

    def fake_device(self, deviceName):
        """
        Hardcodes a fake device
        """
        return {
            "name": deviceName,
            "isOnline": True,
            "deviceOptions": [
                {"optionName": "toggle", "deviceOptionType": "SELECT_ONE", "options": ["ON", "OFF"]},
                {"optionName": "dropDownMenu", "deviceOptionType": "SELECT_ONE", "options": ["dropdown0", "dropdown1", "dropdown2"]},
                {"optionName": "checkboxes", "deviceOptionType": "SELECT_MANY", "options": ["checkbox0", "checkbox1", "checkbox2"]},
                {"optionName": "floatInput0", "deviceOptionType": "USER_INPUT"},
                {"optionName": "floatInput1", "deviceOptionType": "USER_INPUT"},
            ],
        }

    def expected_device(self, deviceName):
        """
        Hardcodes the expected return format of a device query
        """
        return {
            "name": deviceName,
            "isOnline": True,
            "deviceOptions": [
                {"optionName": "toggle", "deviceOptionType": "SELECT_ONE", "userInput": None, "selectOne": None, "selectMany": None, "options": ["ON", "OFF"]},
                {"optionName": "dropDownMenu", "deviceOptionType": "SELECT_ONE", "userInput": None, "selectOne": None, "selectMany": None, "options": ["dropdown0", "dropdown1", "dropdown2"]},
                {"optionName": "checkboxes", "deviceOptionType": "SELECT_MANY", "userInput": None, "selectOne": None, "selectMany": None, "options": ["checkbox0", "checkbox1", "checkbox2"]},
                {"optionName": "floatInput0", "deviceOptionType": "USER_INPUT", "userInput": None, "selectOne": None, "selectMany": None, "options": None},
                {"optionName": "floatInput1", "deviceOptionType": "USER_INPUT", "userInput": None, "selectOne": None, "selectMany": None, "options": None},
            ],
        }

    def post_to_test_client(self, query, variables=None):
        """
        Not a test

        Send an http request to the test client
        """
        response = self.client.post(
            "/graphql/",
            json={"query": query, "variables": variables},
        )
        if response.status_code != 200:
            raise Exception(f"Query failed to run by returning code of {response.status_code}")
        return response.json()

    def test_create_device(self):
        """
        Create devices

        Run GetDevice() to validate device content
        """

        for deviceName in self.deviceNames:
            response = self.post_to_test_client(
                query=CREATE_DEVICE,
                variables={"device": self.fake_device(deviceName)},
            )
            data = response["data"]["createDevice"]
            assert data["success"] and data["modifiedDevice"] == self.expected_device(deviceName)

            response = self.post_to_test_client(
                query=GET_DEVICE,
                variables={"name": deviceName},
            )
            data = response["data"]["getDevice"]
            assert data == self.expected_device(deviceName)

    def test_get_devices(self):
        """
        Retrieve all devices in the database, validate that the devices
        created during this test match expected values
        """
        response = self.post_to_test_client(query=GET_DEVICES)
        data = response["data"]["getDevices"]
        matchesExpected = []
        for deviceQueried in data:
            if deviceQueried['name'] not in self.deviceNames:  # skip devices already in db that are not part of this test
                continue
            matchesExpected.append(deviceQueried == self.expected_device(deviceQueried['name']))
        assert all(matchesExpected) and len(matchesExpected) == len(self.deviceNames)

    def test_update_device(self):
        """
        Updates the content of one device and validates the udpated content
        """
        updated_device = {
            "name": self.deviceNames[0],
            "isOnline": False,
            "deviceOptions": [
                {"optionName": "toggle2", "deviceOptionType": "SELECT_ONE", "options": ["ON", "OFF"]},
            ],
        }
        expected_updated_device = {
            "name": self.deviceNames[0],
            "isOnline": False,
            "deviceOptions": [
                {"optionName": "toggle2", "deviceOptionType": "SELECT_ONE", "userInput": None, "selectOne": None, "selectMany": None, "options": ["ON", "OFF"]},
            ],
        }
        response = self.post_to_test_client(
            query=UPDATE_DEVICE,
            variables={"device": updated_device},
        )
        data = response["data"]["updateDevice"]
        assert data["success"] and data["modifiedDevice"] == expected_updated_device

        response = self.post_to_test_client(
            query=GET_DEVICE,
            variables={"name": self.deviceNames[0]},
        )
        data = response["data"]["getDevice"]
        assert data == expected_updated_device

    def test_delete_device(self):
        """
        Deletes the devices created during this test suite and validates their deletion
        """
        successfulDelete = []
        for deviceName in self.deviceNames:
            response = self.post_to_test_client(
                query=DELETE_DEVICE,
                variables={"name": deviceName},
            )
            successfulDelete.append(response["data"]["deleteDevice"]["success"])
        assert all(successfulDelete)

        response = self.post_to_test_client(query=GET_DEVICES)
        data = response["data"]["getDevices"]

        deviceStillExists = []
        for deviceQueried in data:
            if deviceQueried['name'] in self.deviceNames:
                deviceStillExists.append(deviceQueried['name'])
        assert not deviceStillExists


class TestRunConfig:
    """
    Tests in this suite:

    Create a run configuration file and validate its contents

    Update a run configuration and validate its contents

    Delete the run configuration and validate its deletion

    """

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
            raise Exception(f"Query failed to run by returning code of {response.status_code}")
        return response.json()

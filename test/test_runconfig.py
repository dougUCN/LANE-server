"""
Test queries and mutations related to histograms in the static db
"""

from LANE_server.asgi import application
from starlette.testclient import TestClient
import numpy as np

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

    Test the GetDevices query

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

        Query GetDevice() to validate device content
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

    Test the GetRunConfigs query

    Update a run configuration and validate its contents

    Delete the run configuration and validate its deletion

    """

    client = TestClient(application)  # starlette Test Client instance

    runConfigNames = ["test_config0", "test_config1"]
    runConfigIDs = []
    runConfigFake = {name: None for name in runConfigNames}
    runConfigFakeExpected = {name: None for name in runConfigNames}
    numsteps = 20  # Number of steps per run config

    rng = np.random.default_rng()  # PRNG

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

    def generate_steps(self, numsteps):
        """
        Generates a list `steps_input` for a runconfig with random settings

        returns (`steps_input`, `steps_expected`)

        `steps_input` is suitable for a mutation input, `steps_expected` is what is
        expected by a query
        """
        steps_input = []
        steps_expected = []

        possibleDevices = ['device0', 'device1']
        possibleOptions = [
            {"optionName": "toggle", "deviceOptionType": "SELECT_ONE", "options": ["ON", "OFF"]},
            {"optionName": "dropDownMenu", "deviceOptionType": "SELECT_ONE", "options": ["dropdown0", "dropdown1", "dropdown2"]},
            {"optionName": "checkboxes", "deviceOptionType": "SELECT_MANY", "options": ["checkbox0", "checkbox1", "checkbox2"]},
            {"optionName": "floatInput0", "deviceOptionType": "USER_INPUT"},
            {"optionName": "floatInput1", "deviceOptionType": "USER_INPUT"},
        ]
        possibleOptionsExpected = [
            {"optionName": "toggle", "deviceOptionType": "SELECT_ONE", "userInput": None, "selectOne": None, "selectMany": None, "options": ["ON", "OFF"]},
            {"optionName": "dropDownMenu", "deviceOptionType": "SELECT_ONE", "userInput": None, "selectOne": None, "selectMany": None, "options": ["dropdown0", "dropdown1", "dropdown2"]},
            {"optionName": "checkboxes", "deviceOptionType": "SELECT_MANY", "userInput": None, "selectOne": None, "selectMany": None, "options": ["checkbox0", "checkbox1", "checkbox2"]},
            {"optionName": "floatInput0", "deviceOptionType": "USER_INPUT", "userInput": None, "selectOne": None, "selectMany": None, "options": None},
            {"optionName": "floatInput1", "deviceOptionType": "USER_INPUT", "userInput": None, "selectOne": None, "selectMany": None, "options": None},
        ]

        for i in np.arange(numsteps):
            temp = {}

            if i < numsteps / 3:
                temp["timeFrameOptionType"] = "BEFORE"
            elif i > (numsteps - numsteps / 4):
                temp["timeFrameOptionType"] = "AFTER"
            else:
                temp["timeFrameOptionType"] = "DURING"
            temp["description"] = f"step{i + 1}"
            temp["deviceName"] = self.rng.choice(possibleDevices)
            temp["time"] = int(i)
            index = int(self.rng.integers(low=0, high=len(possibleOptions)))
            temp["deviceOption"] = possibleOptions[index]
            steps_input.append(temp)
            temp["deviceOption"] = possibleOptionsExpected[index]
            steps_expected.append(temp)
        return (steps_input, steps_expected)

    def test_create_config(self):
        """
        Create run config

        Query GetRunConfig to validate device content
        """
        for name in self.runConfigNames:
            steps_input, steps_expected = self.generate_steps(numsteps=self.numsteps)
            self.runConfigFake[name] = {
                "name": name,
                "totalTime": self.numsteps,
                "steps": steps_input,
            }
            self.runConfigFakeExpected[name] = {
                "id": None,
                "name": name,
                "totalTime": self.numsteps,
                "steps": steps_expected,
                "lastLoaded": None,
                "lastSaved": None,
                "priority": 0,
                "status": "NONE",
            }

            response = self.post_to_test_client(
                query=CREATE_RUN_CONFIG,
                variables={"runConfig": self.runConfigFake[name]},
            )
            data = response["data"]["createRunConfig"]
            self.runConfigFakeExpected[name]["id"] = data["modifiedRunConfig"]["id"]
            self.runConfigFakeExpected[name]["lastSaved"] = data["modifiedRunConfig"]["lastSaved"]
            assert data["success"]

            response = self.post_to_test_client(
                query=GET_RUN_CONFIG,
                variables={"id": int(data["modifiedRunConfig"]["id"])},
            )
            data = response["data"]["getRunConfig"]
            assert data == self.runConfigFakeExpected[name]

    def test_get_configs(self):
        """
        Retrieve all run configs in the database, validate that the run configs
        created during this test match expected values
        """
        response = self.post_to_test_client(query=GET_RUN_CONFIGS)
        data = response["data"]["getRunConfigs"]
        assert isinstance(data['canCreateNewRun'], bool)
        matchesExpected = []
        for configQueried in data['runConfigs']:
            if configQueried['name'] not in self.runConfigNames:  # skip devices already in db that are not part of this test
                continue
            matchesExpected.append(configQueried == self.runConfigFakeExpected[configQueried['name']])
        assert all(matchesExpected) and len(matchesExpected) == len(self.runConfigNames)

    def test_update_config(self):
        """
        Updates the content of one run config and validates the updated content
        """
        name = self.runConfigNames[0]
        toUpdate = {
            "id": int(self.runConfigFakeExpected[name]["id"]),
            "priority": 1,
            "status": "QUEUED",
        }
        for key, value in toUpdate.items():
            if key is "id":
                continue
            self.runConfigFakeExpected[name][key] = value

        response = self.post_to_test_client(
            query=UPDATE_RUN_CONFIG,
            variables={"runConfig": toUpdate},
        )
        data = response["data"]["updateRunConfig"]
        self.runConfigFakeExpected[name]["lastSaved"] = data["modifiedRunConfig"]["lastSaved"]

        assert data["success"] and data["modifiedRunConfig"] == self.runConfigFakeExpected[name]

        response = self.post_to_test_client(
            query=GET_RUN_CONFIG,
            variables={"id": int(self.runConfigFakeExpected[name]["id"])},
        )
        data = response["data"]["getRunConfig"]
        assert data == self.runConfigFakeExpected[name]

    def test_delete_configs(self):
        """
        Deletes the configs created during this test suite and validates their deletion
        """
        successfulDelete = []
        configIDs = []
        for _, runConfig in self.runConfigFakeExpected.items():
            configIDs.append(runConfig["id"])
            response = self.post_to_test_client(
                query=DELETE_RUN_CONFIG,
                variables={"id": int(runConfig["id"])},
            )
            successfulDelete.append(response["data"]["deleteRunConfig"]["success"])
        assert all(successfulDelete)

        response = self.post_to_test_client(query=GET_RUN_CONFIGS)
        data = response["data"]["getRunConfigs"]
        assert isinstance(data['canCreateNewRun'], bool)

        configStillExists = []
        for configQueried in data['runConfigs']:
            if configQueried['id'] in configIDs:
                configStillExists.append(configQueried['id'])
        assert not configStillExists

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

    expected_device = {}  # For validation of return value

    def compare_dict(self, expected, received):
        """
        Not a test

        Checks if the values of keys in `expected` match those of `received`
        returns: true if histograms match
        """
        for key, expectedValue in expected.items():
            if received[key] != expectedValue:
                print(f'Mismatch for key "{key}"')
                print(f'expected\n{expectedValue}')
                print(f'received\n{received[key]}')
                return False
        return True

    def spoof_fake_device(self, deviceName):
        """
        Hardcodes a fake device
        """
        return {
            "name": deviceName,
            "isOnline": True,
            "deviceOptions": [
                {"optionName": "toggle", "deviceOptionType": "SELECT_ONE", "options": ["On", "Off"], 'selected': None},
                {"optionName": "dropDownMenu", "deviceOptionType": "SELECT_ONE", "options": ["dropdown0", "dropdown1", "dropdown2"], 'selected': None},
                {"optionName": "checkboxes", "deviceOptionType": "SELECT_MANY", "options": ["checkbox0", "checkbox1", "checkbox2"], 'selected': None},
                {"optionName": "floatInput0", "deviceOptionType": "USER_INPUT", "options": None, 'selected': None},
                {"optionName": "floatInput1", "deviceOptionType": "USER_INPUT", "options": None, 'selected': None},
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
            fake_device = self.spoof_fake_device(deviceName)
            self.expected_device[deviceName] = fake_device.copy()
            self.expected_device['selected'] = None
            response = self.post_to_test_client(
                query=CREATE_DEVICE,
                variables={"device": fake_device},
            )
            data = response["data"]["createDevice"]
            assert data["success"] and self.compare_dict(self.expected_device[deviceName], data["modifiedDevice"])

            response = self.post_to_test_client(
                query=GET_DEVICE,
                variables={"name": deviceName},
            )
            data = response["data"]["getDevice"]
            assert self.compare_dict(self.expected_device[deviceName], data)

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
            matchesExpected.append(self.compare_dict(self.expected_device[deviceQueried['name']], deviceQueried))
        assert all(matchesExpected) and len(matchesExpected) == len(self.deviceNames)

    def test_update_device(self):
        """
        Updates the content of one device and validates the udpated content
        """
        updated_device = {
            "name": self.deviceNames[0],
            "isOnline": False,
            "deviceOptions": [
                {
                    "optionName": "toggle2",
                    "deviceOptionType": "SELECT_ONE",
                    "options": ["On", "Off"],
                    "selected": None,
                },
            ],
        }
        for key, value in updated_device.items():
            self.expected_device[self.deviceNames[0]][key] = value

        response = self.post_to_test_client(
            query=UPDATE_DEVICE,
            variables={"device": updated_device},
        )
        data = response["data"]["updateDevice"]
        assert data["success"] and self.compare_dict(self.expected_device[self.deviceNames[0]], data["modifiedDevice"])

        response = self.post_to_test_client(
            query=GET_DEVICE,
            variables={"name": self.deviceNames[0]},
        )
        data = response["data"]["getDevice"]
        assert self.compare_dict(self.expected_device[self.deviceNames[0]], data)

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
        """
        steps_input = []

        possibleDevices = ['device0', 'device1']
        possibleOptions = [
            {"optionName": "toggle", "deviceOptionType": "SELECT_ONE", "options": ["On", "Off"]},
            {"optionName": "dropDownMenu", "deviceOptionType": "SELECT_ONE", "options": ["dropdown0", "dropdown1", "dropdown2"]},
            {"optionName": "checkboxes", "deviceOptionType": "SELECT_MANY", "options": ["checkbox0", "checkbox1", "checkbox2"]},
            {"optionName": "floatInput0", "deviceOptionType": "USER_INPUT", "options": None},
            {"optionName": "floatInput1", "deviceOptionType": "USER_INPUT", "options": None},
        ]

        for i in np.arange(numsteps):
            temp = {}
            temp["description"] = f"step{i + 1}"
            temp["deviceName"] = self.rng.choice(possibleDevices)
            temp["time"] = int(i)
            index = int(self.rng.integers(low=1, high=len(possibleOptions), endpoint=True))
            temp["deviceOptions"] = possibleOptions[:index]
            # Select a random user option per device Option
            for deviceOption in temp["deviceOptions"]:
                if deviceOption["deviceOptionType"] == "USER_INPUT":
                    deviceOption["selected"] = ["test_string"]
                elif deviceOption["deviceOptionType"] == "SELECT_ONE":
                    deviceOption["selected"] = [self.rng.choice(deviceOption["options"])]
                elif deviceOption["deviceOptionType"] == "SELECT_MANY":
                    deviceOption["selected"] = self.rng.choice(
                        deviceOption["options"],
                        size=int(self.rng.integers(low=1, high=len(deviceOption["options"]))),
                        replace=False,
                    ).tolist()
            steps_input.append(temp)

        return steps_input

    def test_create_config(self):
        """
        Create run config

        Query GetRunConfig to validate device content
        """
        for name in self.runConfigNames:
            steps_input = self.generate_steps(numsteps=self.numsteps)
            self.runConfigFake[name] = {
                "name": name,
                "totalTime": self.numsteps,
                "steps": steps_input,
            }
            self.runConfigFakeExpected[name] = {
                "id": None,
                "name": name,
                "totalTime": self.numsteps,
                "steps": steps_input,
                "lastLoaded": None,
                "lastSaved": None,
                "priority": 0,
                "runConfigStatus": {"status": "READY", "messages": []},
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
            "runConfigStatus": {"status": "QUEUED", "messages": ["Unit test queue"]},
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
        if data['runConfigs'] is not None:
            for configQueried in data['runConfigs']:
                if configQueried['id'] in configIDs:
                    configStillExists.append(configQueried['id'])
        assert not configStillExists

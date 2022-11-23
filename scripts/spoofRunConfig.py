"""
Adds fake devices and runconfigs to the database
"""
import gqlComms as gql
import argparse
import numpy as np

NUM_RUN_CONFIGS = 5
NUM_DEVICES = 3
NUM_STEPS = 10

RNG = np.random.default_rng()
DEVICE_OPTIONS = [
    {"optionName": "Toggle", "deviceOptionType": "SELECT_ONE", "options": ["On", "Off"]},
    {"optionName": "Waveform", "deviceOptionType": "SELECT_ONE", "options": ["Square", "Triangle", "Sine"]},
    {"optionName": "Modifiers", "deviceOptionType": "SELECT_MANY", "options": ["Enable logging", "Wait for trigger", "Ext Clock"]},
    {"optionName": "Frequency", "deviceOptionType": "USER_INPUT"},
    {"optionName": "Amplitude", "deviceOptionType": "USER_INPUT"},
]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-nrc', '--numRunConfigs', type=int, default=NUM_RUN_CONFIGS, help=f'Add this many run configs to the database (default={NUM_RUN_CONFIGS}). Assumes db is empty')
    parser.add_argument('-ns', '--numSteps', type=int, default=NUM_STEPS, help=f'Number of steps per run config (default={NUM_STEPS})')
    parser.add_argument('-nd', '--numDevices', type=int, default=NUM_DEVICES, help=f'Number of devices to spoof (default={NUM_DEVICES})')
    args = parser.parse_args()

    possibleDevices = [f'Signal Generator{i}' for i in np.arange(args.numDevices)]

    print('Creating fake devices')
    for deviceName in possibleDevices:
        device = {"name": deviceName, "isOnline": True, "deviceOptions": DEVICE_OPTIONS}
        gql.createDevice(device)

    print('Creating fake runConfigs')
    for i in np.arange(args.numRunConfigs):
        runConfig = {
            "name": f"config{i}",
            "totalTime": args.numSteps + 10,
            "steps": generate_steps(args.numSteps, possibleDevices),
        }
        gql.createRunConfig(runConfig)

    print('Done')


def generate_steps(numsteps, possibleDevices):
    """
    Generates a list `steps_input` for a runconfig with random settings
    """
    steps_input = []

    for i in np.arange(numsteps):
        temp = {}
        temp["description"] = f"step{i + 1}"
        temp["deviceName"] = RNG.choice(possibleDevices)
        temp["time"] = int(i)
        index = int(RNG.integers(low=1, high=len(DEVICE_OPTIONS), endpoint=True))
        temp["deviceOptions"] = DEVICE_OPTIONS[:index]
        # Select a random user option per device option
        for deviceOption in temp["deviceOptions"]:
            if deviceOption["deviceOptionType"] == "USER_INPUT":
                deviceOption["selected"] = ["test_string_value"]
            elif deviceOption["deviceOptionType"] == "SELECT_ONE":
                deviceOption["selected"] = [RNG.choice(deviceOption["options"])]
            elif deviceOption["deviceOptionType"] == "SELECT_MANY":
                deviceOption["selected"] = RNG.choice(
                    deviceOption["options"],
                    size=int(RNG.integers(low=1, high=len(deviceOption["options"]))),
                    replace=False,
                ).tolist()
        steps_input.append(temp)

    return steps_input


if __name__ == "__main__":
    main()

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
    {"optionName": "toggle", "deviceOptionType": "SELECT_ONE", "options": ["On", "Off"]},
    {"optionName": "dropDownMenu", "deviceOptionType": "SELECT_ONE", "options": ["dropdown0", "dropdown1", "dropdown2"]},
    {"optionName": "checkboxes", "deviceOptionType": "SELECT_MANY", "options": ["checkbox0", "checkbox1", "checkbox2"]},
    {"optionName": "floatInput0", "deviceOptionType": "USER_INPUT"},
    {"optionName": "floatInput1", "deviceOptionType": "USER_INPUT"},
]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-nrc', '--numRunConfigs', type=int, default=NUM_RUN_CONFIGS, help=f'Add this many run configs to the database (default={NUM_RUN_CONFIGS}). Assumes db is empty')
    parser.add_argument('-ns', '--numSteps', type=int, default=NUM_STEPS, help=f'Number of steps per run config (default={NUM_STEPS})')
    parser.add_argument('-nd', '--numDevices', type=int, default=NUM_DEVICES, help=f'Number of devices to spoof (default={NUM_DEVICES})')
    args = parser.parse_args()

    possibleDevices = [f'device{i}' for i in np.arange(args.numDevices)]

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

        if i < numsteps / 3:
            temp["timeFrameOptionType"] = "BEFORE"
        elif i > (numsteps - numsteps / 4):
            temp["timeFrameOptionType"] = "AFTER"
        else:
            temp["timeFrameOptionType"] = "DURING"
        temp["description"] = f"step{i + 1}"
        temp["deviceName"] = RNG.choice(possibleDevices)
        temp["time"] = int(i)
        index = int(RNG.integers(low=0, high=len(DEVICE_OPTIONS)))
        temp["deviceOption"] = DEVICE_OPTIONS[index]
        # Select a random user option
        if temp["deviceOption"]["deviceOptionType"] == "USER_INPUT":
            temp["deviceOption"]["selected"] = ["test_string"]
        elif temp["deviceOption"]["deviceOptionType"] == "SELECT_ONE":
            temp["deviceOption"]["selected"] = [RNG.choice(temp["deviceOption"]["options"])]
        elif temp["deviceOption"]["deviceOptionType"] == "SELECT_MANY":
            temp["deviceOption"]["selected"] = RNG.choice(
                temp["deviceOption"]["options"],
                size=int(RNG.integers(low=1, high=len(temp["deviceOption"]["options"]))),
                replace=False,
            ).tolist()
        steps_input.append(temp)

    return steps_input


if __name__ == "__main__":
    main()

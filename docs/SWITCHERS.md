# Switchers

This documents use of the python switcher interface code
in `worker_threads/slow_control_worker/switcher`

Switcher 1 serial no: "A105HOY5"

Switcher 2 serial no: "A5052RD1"

Upon disconnecting/powering off the switchers from the computer,
run ./SETUP_SWITCHERS to automatically detect what serial ports the
switchers are on and to set up symbolic links automatically

Using a switcher should be as simple as

```
from switcher import dxlS500R # Assuming you are in the same directory as the switcher package
motor = dxlS500R(PORT='/path/to/symbolic/link',VERBOSE=True)
motor.ping() # or any other command in the library documentation below
```

## Note on motor model

This code is for interfacing with the Dynamixel Pro h54-200-s500-r.
(Note that the switchers for the UCNA experiment at LANL use different motors)

For a different model of motor you will likely need to alter the register values
in `switcher/globals.py` according to the online manual for the corresponding motor

## Switcher library documentation

```
NAME
    switcher

PACKAGE CONTENTS
    device
    dynamixel_sdk (package)
    globals

CLASSES
    builtins.object
        switcher.device.dxlS500R

    class dxlS500R(builtins.object)
     |  Device interface with the Dynamixel Pro h54-200-s500-r
     |
     |  Methods defined here:
     |
     |  __init__(self, PORT='/dev/ttyUSB0', DXL_ID=1, BAUDRATE=57600, VERBOSE=False)
     |      PORT expects some /dev/ttyUSB*
     |      DXL_ID can be determined with /tests/ping.py. Factory default is 1
     |      BAUDRATE is set to factory default
     |      If VERBOSE is True, prints out status updates
     |
     |  checkCommStatus(self, dxl_comm_result, dxl_error)
     |      Takes output status from packet handler and interprets it.
     |      Raises error if unsuccessful
     |
     |  close(self, disengage_motor=False)
     |      Disengages motor and closes communication port
     |
     |  disable_torque(self)
     |      Disengages the motor
     |
     |  enable_torque(self)
     |      Enables torque on motor
     |
     |  get_control_mode(self)
     |      Returns the control mode that the motor is operating in
     |
     |  get_current_position(self, IN_TICS=False)
     |      Returns current position [degrees] (default) or in [tics]. Note: Never returns a negative value
     |
     |  get_current_velocity(self)
     |      Returns current velocity [deg/sec] (This is "Before reduction gears" whatever that means)
     |
     |  get_goal_torque(self)
     |      set goal torque on motor
     |
     |  get_goal_velocity(self)
     |      Returns goal velocity [deg/sec] (This is "Before reduction gears" whatever that means)
     |
     |  get_id(self)
     |      Returns ID of connected motor
     |
     |  is_moving(self)
     |      Returns 1 if motor is in motion
     |
     |  one_way_turn_to(self, pos, IN_TICS=False)
     |      Forces the switcher to turn in the positive direction only to reach a new position
     |
     |  ping(self)
     |      Pings communication port and retrieves model number
     |
     |  pprint(self, msg)
     |      Prints motor status updates if VERBOSE = True
     |
     |  reboot(self)
     |      Reboots motor. Dynamixel LED will flicker
     |
     |  set_control_mode(self, mode)
     |      Set to "TorqueControl", "VelocityControl", "PositionControl" (default), or "ExtendedPositionControl" (multi-turn enabled) mode
     |
     |  set_goal_torque(self, goal_torque)
     |      set goal torque on motor
     |
     |  set_id(self, newID)
     |      Sets ID of connected motor to a value
     |
     |  set_position(self, pos, IN_TICS=False)
     |      Sets current position in [degrees] (default) or in [tics]
     |
     |  set_velocity(self, deg_per_sec)
     |      Sets goal velocity [deg/sec] (This is "Before reduction gears" whatever that means)
     |      Note that a value of 0 [default] sets velocity to the max
```

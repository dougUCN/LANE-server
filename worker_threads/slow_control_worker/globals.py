#!/usr/bin/env python
import numpy as np
import time
import os

RH_GATE_VALVE_OPEN_STATE = 0
RH_GATE_VALVE_CLOSE_STATE = 1
IV2_GATE_VALVE_OPEN_STATE = 1
IV2_GATE_VALVE_CLOSE_STATE = 0
BEAM_ON = 0  # since the signal we get is the veto
BEAM_OFF = 1
ADDR_EIO0 = 8
ADDR_EIO1 = 9
ADDR_EIO2 = 10
ADDR_EIO3 = 11
ADDR_EIO4 = 12
ADDR_EIO5 = 13
ADDR_EIO6 = 14
ADDR_EIO7 = 15
ADDR_EIO8 = 16
ADDR_EIO9 = 17

MOTOR_VELOCITY = 50
SWITCHER1_COMM_PORT = f'{os.getcwd()}/ports/switcher1'
SWITCHER2_COMM_PORT = f'{os.getcwd()}/ports/switcher2'

TICS_TO_DEG = 180 / 250961.5

# Switcher 1 coords (Higher switcher)
S1_STRAIGHT = [484842, 735800]  # Location in tics
S1_TEST = [170600, 421300]
S1_DUMP = [547100, 798000]

# Switcher 2 coords (Lower switcher)
S2_STRAIGHT = [94400, 344463]  # Location in tics
S2_TEST = [533900, 784600]
S2_DUMP = [408500, 659000]

# hide all my labjack and switcher interface functions here to keep python runscripts minimal
def isBeamEnabled(labjack):
    return labjack.getFIOState(5) == BEAM_ON


def turnSwitcher(switcher, configuration):
    '''Does a one way turn of the switcher to the closest value in a list of configurations'''
    nextPos = findClosestTurn(switcher, configuration)
    switcher.one_way_turn_to(nextPos, IN_TICS=True)
    return nextPos


def waitForSwitcherMove(switcher1, switcher2):
    while switcher1.is_moving() or switcher2.is_moving():
        time.sleep(0.1)


def findClosestTurn(switcher, validPositions):
    '''Given a list validPositions of positions, finds the one closest to current position'''
    current = switcher.get_current_position(IN_TICS=True)
    for pos in np.sort(validPositions):
        if pos >= current:
            return pos
    return np.amin(validPositions)


def openTriumfGV(labjack):
    '''Requires 24V DC on the labjack'''
    labjack.setDOState(ADDR_EIO6, IV2_GATE_VALVE_OPEN_STATE)


def closeTriumfGV(labjack):
    '''Requires 24V DC on the labjack'''
    labjack.setDOState(ADDR_EIO6, IV2_GATE_VALVE_CLOSE_STATE)


def openRHGV(labjack):
    '''Requires 24V DC'''
    labjack.setDOState(ADDR_EIO5, RH_GATE_VALVE_OPEN_STATE)


def closeRHGV(labjack):
    '''Requires 24V DC'''
    labjack.setDOState(ADDR_EIO5, RH_GATE_VALVE_CLOSE_STATE)

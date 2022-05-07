from .dynamixel_sdk import *
import sys
from .globals import *

class dxlS500R:
    '''Device interface with the Dynamixel Pro h54-200-s500-r'''
    PROTOCOL_VERSION = 2.0

    def __init__(self, PORT= '/dev/ttyUSB0', DXL_ID = 1, BAUDRATE = 57600, VERBOSE=False):
        '''PORT expects some /dev/ttyUSB*
        DXL_ID can be determined with /tests/ping.py. Factory default is 1
        BAUDRATE is set to factory default
        If VERBOSE is True, prints out status updates
        '''
        self.portHandler = PortHandler(PORT)
        self.ID = DXL_ID
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)
        self.verbose = VERBOSE

        # Open port
        if self.portHandler.openPort():
            self.pprint('Port opened')
        else:
            raise dxlS500R_Exception(f'Failed to open port {PORT}')

        # Set baudrate
        if self.portHandler.setBaudRate(BAUDRATE):
            self.pprint(f'Baudrate set to {BAUDRATE}')
        else:
            raise dxlS500R_Exception('Unable to set baudrate')

        # Check control mode
        self.extendedPositionControl = (self.get_control_mode == 'ExtendedPositionControl')

        self.enable_torque()
    
    def pprint(self, msg):
        '''Prints motor status updates if VERBOSE = True'''
        if self.verbose:
            print(msg)

    def one_way_turn_to(self, pos, IN_TICS=False):
        '''Forces the switcher to turn in the positive direction only to reach a new position'''
        if IN_TICS and not (pos >= MIN_POS_LIMIT):
            raise dxlS500R_Exception(f'pos must be > {MIN_POS_LIMIT} tics')
        elif not IN_TICS and not (pos >= -180):
            raise dxlS500R_Exception('pos must be > -180 degrees')

        newPosition = pos
        currentPosition = self.get_current_position(IN_TICS=IN_TICS)

        if newPosition > currentPosition:
            self.set_position(newPosition, IN_TICS=IN_TICS)
        else:
            self.set_control_mode('PositionControl') # Current position gets translated to [-180,180]
            currentPosition = self.get_current_position(IN_TICS=IN_TICS)

            if IN_TICS:
                if currentPosition >= (POSITION_LIMIT_32 * 2) + MIN_POS_LIMIT: # means current position is [MIN_POS_LIMIT, 0)
                    currentPosition -= POSITION_LIMIT_32 * 2
                if newPosition < currentPosition:
                    newPosition += MAX_POS_LIMIT*2
            else:
                if currentPosition >= MAX_EXTENDED_POSITION - 180: # means current position is [-180, 0)
                    currentPosition -= MAX_EXTENDED_POSITION
                if newPosition < currentPosition:
                    newPosition += 360
            self.set_control_mode('ExtendedPositionControl')
            self.set_position(newPosition, IN_TICS=IN_TICS)

        self.pprint(f'current: {currentPosition}, new: {newPosition}')

    def enable_torque(self):
        '''Enables torque on motor'''
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.ID, ADDR_TORQUE_ENABLE, TORQUE_ON)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        self.pprint('Device torque enabled')

    def disable_torque(self):
        '''Disengages the motor'''
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.ID, ADDR_TORQUE_ENABLE, TORQUE_OFF)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        self.pprint('Device torque disabled')

    def set_goal_torque(self, goal_torque):
        '''set goal torque on motor'''
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, self.ID, ADDR_GOAL_TORQUE, goal_torque)
        self.checkCommStatus(dxl_comm_result, dxl_error)

    def get_goal_torque(self):
        '''set goal torque on motor'''
        dxl_read_value, dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(self.portHandler, self.ID, ADDR_GOAL_TORQUE)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        return dxl_read_value 

    def get_current_velocity(self):
        '''Returns current velocity [deg/sec] (This is "Before reduction gears" whatever that means)'''
        dxl_read_value, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, self.ID, ADDR_PRESENT_VELOCITY)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        return dxl_read_value / VEL_SCALE_FACTOR

    def set_velocity(self, deg_per_sec):
        '''Sets goal velocity [deg/sec] (This is "Before reduction gears" whatever that means)
        Note that a value of 0 [default] sets velocity to the max'''
        tics = int(deg_per_sec * VEL_SCALE_FACTOR)
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, self.ID, ADDR_GOAL_VELOCITY, tics)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        self.pprint(f'Velocity set to {deg_per_sec}')

    def get_goal_velocity(self):
        '''Returns goal velocity [deg/sec] (This is "Before reduction gears" whatever that means)'''
        dxl_read_value, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, self.ID, ADDR_GOAL_VELOCITY)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        return dxl_read_value / VEL_SCALE_FACTOR

    def get_current_position(self, IN_TICS=False):
        '''Returns current position [degrees] (default) or in [tics]. Note: Never returns a negative value'''
        dxl_read_value, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, self.ID, ADDR_PRESENT_POSITION)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        if IN_TICS:
            return dxl_read_value 
        else:
            return dxl_read_value * POS_SCALE_FACTOR 

    def set_position(self, pos, IN_TICS=False):
        '''Sets current position in [degrees] (default) or in [tics]'''
        if IN_TICS:
            tics = pos
        else:
            tics = int(pos/POS_SCALE_FACTOR)
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, self.ID, ADDR_GOAL_POSITION, tics)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        self.pprint(f'Position set to {pos}')

    def is_moving(self):
        '''Returns 1 if motor is in motion'''
        dxl_read_value, dxl_comm_result, dxl_error = self.packetHandler.read1ByteTxRx(self.portHandler, self.ID, ADDR_MOVING)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        return dxl_read_value

    def get_control_mode(self):
        '''Returns the control mode that the motor is operating in'''
        dxl_read_value, dxl_comm_result, dxl_error = self.packetHandler.read1ByteTxRx(self.portHandler, self.ID, ADDR_OP_MODE)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        if dxl_read_value == 3:
            self.extendedPositionControl = True
        else:
            self.extendedPositionControl = False
        return list(OPERATING_MODES.keys())[list(OPERATING_MODES.values()).index(int(dxl_read_value))]

    def set_control_mode(self, mode):
        '''Set to "TorqueControl", "VelocityControl", "PositionControl" (default), or "ExtendedPositionControl" (multi-turn enabled) mode'''
        if mode not in OPERATING_MODES.keys():
            raise dxlS500R_Exception(f"{mode} is not a valid control mode\nOptions: {OPERATING_MODES.keys()}")        
        self.disable_torque() # Writing to ROM not permitted without disabling torque
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.ID, ADDR_OP_MODE, OPERATING_MODES[mode])
        self.checkCommStatus(dxl_comm_result, dxl_error)
        if mode != 'ExtendedPositionControl':
            self.extendedPositionControl = False
        self.pprint(f"Control mode set to {mode}")
        self.enable_torque()

    def get_id(self):
        '''Returns ID of connected motor'''
        dxl_read_value, dxl_comm_result, dxl_error = self.packetHandler.read1ByteTxRx(self.portHandler, self.ID, ADDR_ID)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        return dxl_read_value

    def set_id(self, newID):
        '''Sets ID of connected motor to a value'''
        self.disable_torque() # Writing to ROM not permitted without disabling torque
        if not (0 <= newID <= 254):
            raise dxlS500R_Exception(f'{newID} is an invalid value. newID must be = [0, 253]')
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.ID, ADDR_ID, newID)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        self.ID = newID
        self.pprint(f'Motor ID set to {self.ID}')
        self.enable_torque()

    def ping(self):
        '''Pings communication port and retrieves model number'''
        dxl_model_number, dxl_comm_result, dxl_error = self.packetHandler.ping(self.portHandler, self.ID)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        self.pprint(f"pong -- Dynamixel model number : {dxl_model_number}")
        return f"{dxl_model_number}"

    def reboot(self):
        '''Reboots motor. Dynamixel LED will flicker'''
        dxl_comm_result, dxl_error = self.packetHandler.reboot(self.portHandler, self.ID)
        self.checkCommStatus(dxl_comm_result, dxl_error)
        self.pprint("Reboot succeeded")

    def close(self, disengage_motor = False):
        '''Disengages motor and closes communication port'''
        if disengage_motor:
            self.disable_torque()
        self.portHandler.closePort()
        self.pprint("Communication port closed")

    def checkCommStatus(self, dxl_comm_result, dxl_error):
        '''Takes output status from packet handler and interprets it.
        Raises error if unsuccessful
        '''
        if dxl_comm_result != COMM_SUCCESS:
            raise dxlS500R_Exception("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            raise dxlS500R_Exception("%s" % self.packetHandler.getRxPacketError(dxl_error))


class dxlS500R_Exception(Exception):
    '''Custom dxlS500R Exceptions'''
    pass

# Address registers and misc values for the dynamixel pro H54-200-S500-R
#
# For whatever awful reason, the incorrect registers are listed at
# https://emanual.robotis.com/docs/en/dxl/pro/h54-200-s500-r/
#
# Registers are based off the ones listed here
# https://emanual.robotis.com/docs/en/dxl/pro/l54-30-s400-r/

# Address name          address         Byte size   Read/Write
ADDR_ID                 = 7             # 1         RW
ADDR_OP_MODE            = 11            # 1         RW
ADDR_TORQUE_ENABLE      = 562           # 1         RW
ADDR_LED_RED            = 563           # 1         RW
ADDR_LED_GREEN          = 564           # 1         RW
ADDR_LED_BLUE           = 565           # 1         RW
ADDR_VELOCITY_I_GAIN    = 586           # 2         RW
ADDR_VELOCITY_P_GAIN    = 588           # 2         RW
ADDR_POSITION_P_GAIN    = 594           # 2         RW
ADDR_GOAL_POSITION      = 596           # 4         RW
ADDR_GOAL_VELOCITY      = 600           # 4         RW
ADDR_GOAL_TORQUE        = 604           # 2         RW
ADDR_GOAL_ACCEL         = 606           # 4         RW
ADDR_MOVING             = 610           # 1         R
ADDR_PRESENT_POSITION   = 611           # 4         R
ADDR_PRESENT_VELOCITY   = 615           # 4         R
ADDR_PRESENT_CURRENT    = 621           # 2         R
ADDR_PRESENT_INPUT_VOLT = 623           # 2         R
ADDR_PRESENT_TEMP       = 625           # 1         R

# Other
TORQUE_ON = 1
TORQUE_OFF = 0
VELOCITY_LIMIT_32 = 2147483647  # Velocity should be 32 bits
POSITION_LIMIT_32 = 2147483647  # Position should be 32 bits
VEL_SCALE_FACTOR = 60  # Converts motor velocity deg/s to tics
POS_SCALE_FACTOR = 180 / 250961.5   # Converts motor position tics to deg. Hand-callibrated value
MAX_EXTENDED_POSITION = POSITION_LIMIT_32 * 2 * POS_SCALE_FACTOR # = Max allowed position [degrees]
ACC_SCALE_FACTOR = 58000        # Converts motor acceleration tics to rev/min^2
MIN_POS_LIMIT = -250961         # Minimum allowed position (Ignored when in Extended Position Control mode
MAX_POS_LIMIT = 250961          # Max allowed position (Ignored when in Extended Position Control mode
TRUE_POS_LIMIT = 2147483647     # True position value range when Extended position control mode is on

# Operating modes
OPERATING_MODES =  {'TorqueControl':0,
                    'VelocityControl':1,
                    'PositionControl':3,
                    'ExtendedPositionControl':4}

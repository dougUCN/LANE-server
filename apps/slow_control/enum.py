from ariadne import EnumType
from .common import (
    RunState,
    TimeFrame,
    DeviceOption,
)

run_config_status_enum = EnumType("RunStatus", RunState)

time_frame_option_enum = EnumType("TimeFrameOption", TimeFrame)

device_option_enum = EnumType("DeviceOption", DeviceOption)

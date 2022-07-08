from ariadne import EnumType
from .common import (
    RunState,
    TimeFrame,
    DeviceOption,
)

run_config_status_enum = EnumType("RunConfigStatusEnum", RunState)

time_frame_option_enum = EnumType("TimeFrameOptionEnum", TimeFrame)

device_option_enum = EnumType("DeviceOptionEnum", DeviceOption)

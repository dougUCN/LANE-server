from ariadne import EnumType
from .common import (
    RunState,
    DeviceOption,
)

run_config_status_enum = EnumType("RunConfigStatusEnum", RunState)

device_option_enum = EnumType("DeviceOptionEnum", DeviceOption)

from ariadne import ScalarType
from dateutil.parser import parse as dateutilParse
from django.utils.timezone import make_aware
import json

"""
Datetime scalar taken from
https://ariadnegraphql.org/docs/scalars
"""

datetime_scalar = ScalarType("Datetime")


@datetime_scalar.serializer
def serialize_datetime(value):
    '''Scalar passed through this function before returned to client'''
    return value.isoformat()


@datetime_scalar.value_parser
def parse_datetime_value(value):
    '''Will be used when scalar value is passed as part of query variables'''
    dt = dateutilParse(value)
    if dt.tzinfo is None:  # Convert unaware datetimes into aware ones
        return make_aware(dt)
    else:
        return dt

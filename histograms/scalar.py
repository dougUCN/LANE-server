from ariadne import ScalarType
from dateutil.parser import parse as dateParse
from django.utils.timezone import make_aware

"""Datetime scalar taken from
https://ariadne.readthedocs.io/en/0.1.0/scalars.html
"""

datetime_scalar = ScalarType("Datetime")

@datetime_scalar.serializer
def serialize_datetime(value):
    '''Datetime passed through this function before returned to client'''
    return value.isoformat()

@datetime_scalar.value_parser
def parse_datetime_value(value):
    '''Will be used when scalar value is passed as part of query variables'''
    if value:
        return make_aware( dateParse(value) )

@datetime_scalar.literal_parser
def parse_datetime_literal(ast):
    '''Will be used when scalar value is passed as part of query content'''
    value = str(ast.value)
    return parse_datetime_value(value)
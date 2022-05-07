from ariadne import ScalarType
from dateutil.parser import parse as dateParse
from django.utils.timezone import make_aware

"""Datetime scalar taken from
https://ariadnegraphql.org/docs/scalars
"""

datetime_scalar = ScalarType("Datetime")

@datetime_scalar.serializer
def serialize_datetime(value):
    return value.isoformat()

@datetime_scalar.value_parser
def parse_datetime_value(value):
    if value:
        return dateParse(value)

@datetime_scalar.literal_parser
def parse_datetime_literal(ast):
    value = str(ast.value)
    return make_aware( parse_datetime_value(value) )
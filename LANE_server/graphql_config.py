from ariadne import make_executable_schema, load_schema_from_path, gql

from apps.histograms.query import query as h_query
from apps.histograms.mutation import mutation as h_mutation
from apps.histograms.subscription import subscription as h_subscription
from apps.histograms.scalar import datetime_scalar

from apps.slow_control.query import query as s_query
from apps.slow_control.mutation import mutation as s_mutation
from apps.slow_control.subscription import subscription as s_subscription
from apps.slow_control.enum import run_status_enum

schema_files = [
    "schema/schema.graphql",
    "schema/histograms.graphql",
    "schema/slow_control.graphql",
    "schema/pagination.graphql",
]

type_defs = []

for file in schema_files:
    type_defs.append(gql(load_schema_from_path(file)))

schema = make_executable_schema(
    type_defs,
    h_query,
    h_mutation,
    h_subscription,
    datetime_scalar,
    s_query,
    s_mutation,
    s_subscription,
    run_status_enum,
)

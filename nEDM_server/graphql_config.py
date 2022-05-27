from ariadne import make_executable_schema, load_schema_from_path, gql

from histograms.query import query as h_query
from histograms.mutation import mutation as h_mutation
from histograms.subscription import subscription as h_subscription
from histograms.scalar import datetime_scalar

from slow_control.query import query as s_query
from slow_control.mutation import mutation as s_mutation
from slow_control.subscription import subscription as s_subscription
from slow_control.enum import run_status_enum

schema_files = [
    "nEDM_server/schema.graphql",
    "histograms/schema.graphql",
    "slow_control/schema.graphql",
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

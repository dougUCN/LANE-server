from ariadne import make_executable_schema, load_schema_from_path, gql
from histograms.query import query as h_query
from histograms.mutation import mutation as h_mutation
from histograms.subscription import subscription as h_subscription
from histograms.scalar import datetime_scalar
from ariadne_jwt import GenericScalar
from users.schema import mutation as u_mutation

schema_files = ["nEDM_server/schema.graphql", 
                "histograms/schema.graphql",
                "users/schema.graphql",
                "slow_control/schema.graphql",
                ]

type_defs = []

for file in schema_files:
    type_defs.append( gql( load_schema_from_path(file) ) )

schema = make_executable_schema(type_defs, 
                                h_query, h_mutation, h_subscription,
                                u_mutation, GenericScalar,
                                datetime_scalar,)

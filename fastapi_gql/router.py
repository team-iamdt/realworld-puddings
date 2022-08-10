from fastapi import Depends

from fastapi_gql.utils.is_debug import is_debug

import strawberry
from strawberry.extensions import ParserCache
from strawberry.extensions import QueryDepthLimiter
from strawberry.extensions import ValidationCache
from strawberry.fastapi import BaseContext
from strawberry.fastapi import GraphQLRouter
from strawberry.tools import create_type
from strawberry.tools import merge_types

__all__ = ["graphql_apps"]

# -- AuthN Related APIs --
SignMutation = create_type("SignMutation", [])

sign_schema = strawberry.Schema(
    query=create_type("SignQuery", []),
    mutation=SignMutation,
    extensions=[
        ParserCache(),
        ValidationCache(),
    ],
)

sign_graphql_app = GraphQLRouter(
    sign_schema,
    graphiql=is_debug(),
)


# -- Any APIs Without AuthN Related --
class AppContext(BaseContext):
    def __init__(self):
        super().__init__()


def resolve_app_context_dependency() -> AppContext:
    return AppContext()


async def get_app_context(
    custom_context=Depends(resolve_app_context_dependency),
):
    return custom_context


Query = merge_types("Query", ())
Mutation = merge_types("Mutation", ())

default_schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        ParserCache(),
        ValidationCache(),
        QueryDepthLimiter(max_depth=10),
    ],
)

default_graphql_app = GraphQLRouter(
    default_schema,
    context_getter=get_app_context,
    graphiql=is_debug(),
)

# Export this only.
graphql_apps = (sign_graphql_app, default_graphql_app)

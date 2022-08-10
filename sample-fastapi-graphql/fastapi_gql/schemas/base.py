import strawberry
from strawberry.extensions import (
    ParserCache,
    QueryDepthLimiter,
    ValidationCache,
)

__all__ = ["schema"]


@strawberry.type
class Query:
    pass


@strawberry.type
class Mutation:
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        ParserCache(),
        ValidationCache(),
        QueryDepthLimiter(max_depth=10),
    ],
)

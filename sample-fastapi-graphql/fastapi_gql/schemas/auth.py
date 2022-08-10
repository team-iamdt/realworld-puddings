from fastapi_gql.models.type.users import TokenResponse, UserModel
from fastapi_gql.resolvers import users_sign
import strawberry
from strawberry.extensions import ParserCache, ValidationCache

__all__ = ["schema"]


@strawberry.type
class Query:
    validate: UserModel = strawberry.field(resolver=users_sign.validate)


@strawberry.type
class Mutation:
    sign_in: TokenResponse = strawberry.mutation(resolver=users_sign.sign_in)
    sign_up: TokenResponse = strawberry.mutation(resolver=users_sign.sign_up)
    refresh: TokenResponse = strawberry.mutation(resolver=users_sign.refresh)


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        ParserCache(),
        ValidationCache(),
    ],
)

import os
from typing import Dict

from dotenv import dotenv_values
from edgedb import AsyncIOClient, create_async_client
from fastapi import Depends
from fastapi_gql.dataloaders.users import create_user_data_loader
from fastapi_gql.errors.missing_dependency_error import MissingDependencyError
from fastapi_gql.models.type.users import UserModel
from fastapi_gql.utils.is_debug import is_debug
import strawberry
from strawberry.dataloader import DataLoader
from strawberry.extensions import (
    ParserCache,
    QueryDepthLimiter,
    ValidationCache,
)
from strawberry.fastapi import BaseContext, GraphQLRouter
from strawberry.tools import create_type, merge_types

__all__ = ["graphql_apps", "on_shutdown", "BaseAppContext", "AppContext"]


def get_initial_dependencies():
    path_of_dotenv = os.environ.get("APP_ENV_PATH")
    if path_of_dotenv is None:
        raise MissingDependencyError("APP_ENV_PATH")

    config = {
        **dotenv_values(path_of_dotenv),
        **os.environ,
    }

    edgedb_dsn = config.get("EDGEDB_DSN")
    if edgedb_dsn is None:
        raise MissingDependencyError("EDGEDB_DSN")

    client = create_async_client(edgedb_dsn)

    return config, client


(app_config, edgedb_client) = get_initial_dependencies()


# -- Context Related --
# BaseAppContext is only used for AuthN related GraphQL APIs.
# Other GraphQL API's Contexts inherits this BaseAppContext.
class BaseAppContext(BaseContext):
    config: Dict[str, str | None]  # config from dotenv
    client: AsyncIOClient  # connection from edgedb
    user_data_loader: DataLoader[int, UserModel | None]  # data loader for user

    def __init__(
        self,
        config: Dict[str, str | None],
        client: AsyncIOClient,
        user_data_loader: DataLoader[int, UserModel | None],
    ):
        super().__init__()
        self.config = config
        self.client = client
        self.user_data_loader = user_data_loader


# -- AuthN Related APIs --
def resolve_auth_app_context_dependency() -> BaseAppContext:
    user_data_loader = create_user_data_loader(
        client=edgedb_client,
    )

    return BaseAppContext(
        config=app_config,
        client=edgedb_client,
        user_data_loader=user_data_loader,
    )


async def get_auth_app_context(
    custom_context=Depends(resolve_auth_app_context_dependency),
):
    return custom_context


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
    context_getter=get_auth_app_context,
)


# -- Any APIs Without AuthN Related --
class AppContext(BaseAppContext):
    pass


def resolve_app_context_dependency() -> AppContext:
    user_data_loader = create_user_data_loader(
        client=edgedb_client,
    )

    return AppContext(
        config=app_config,
        client=edgedb_client,
        user_data_loader=user_data_loader,
    )


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


# shutdown event
async def on_shutdown():
    await edgedb_client.aclose()


graphql_apps = (sign_graphql_app, default_graphql_app)

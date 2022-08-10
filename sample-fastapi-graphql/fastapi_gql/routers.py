import os

from dotenv import dotenv_values
from edgedb import create_async_client
from fastapi import Depends
from fastapi_gql.contexts import BaseAppContext
from fastapi_gql.dataloaders.users import create_user_data_loader
from fastapi_gql.errors.missing_dependency_error import MissingDependencyError
from fastapi_gql.schemas.auth import schema as auth_schema
from fastapi_gql.utils.is_debug import is_debug
from strawberry.fastapi import GraphQLRouter

# from fastapi_gql.schemas.base import schema as base_schema

__all__ = ["graphql_apps", "on_shutdown"]


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

    client = create_async_client(edgedb_dsn, tls_security="insecure")

    return config, client


(app_config, edgedb_client) = get_initial_dependencies()


# -- Context Related --

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


sign_graphql_app = GraphQLRouter(
    schema=auth_schema,
    graphiql=is_debug(),
    context_getter=get_auth_app_context,
)


# # -- Any APIs Without AuthN Related --
# def resolve_app_context_dependency() -> AppContext:
#     user_data_loader = create_user_data_loader(
#         client=edgedb_client,
#     )
#
#     return AppContext(
#         config=app_config,
#         client=edgedb_client,
#         user_data_loader=user_data_loader,
#     )
#
#
# async def get_app_context(
#     custom_context=Depends(resolve_app_context_dependency),
# ):
#     return custom_context
#
#
# default_graphql_app = GraphQLRouter(
#     schema=base_schema,
#     context_getter=get_app_context,
#     graphiql=is_debug(),
# )


# shutdown event
async def on_shutdown():
    await edgedb_client.aclose()


# graphql_apps = (sign_graphql_app, default_graphql_app)
graphql_apps = (sign_graphql_app,)

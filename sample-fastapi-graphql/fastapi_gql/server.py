from typing import Any, List, Tuple

import click
from fastapi import FastAPI
from fastapi_gql.routers import graphql_apps, on_shutdown
import uvicorn

# Initialize FastAPI
(auth,) = graphql_apps
# (auth, default) = graphql_apps

app = FastAPI()
app.on_event("shutdown")(on_shutdown)
app.include_router(auth, prefix="/graphql/auth")
# app.include_router(default, prefix="/graphql")


# Apply Default Values for Click Command Group
def default_bind(value: dict):
    def _inner(fn: Any):
        fn.default_map_value = value
        return fn

    return _inner


def merge_default_maps(groups: List[Any] | Tuple[Any]):
    return {
        _group.name: _group.default_map_value
        for _group in groups
        if hasattr(_group, "name") and hasattr(_group, "default_map_value")
    }


# Setup Click-related Commands
@default_bind({"app": "fastapi_gql.server:app", "port": "8080"})
@click.group("run")
def cli_uvicorn():
    pass


# invoke cli_main.
if __name__ == "__main__":
    cli_uvicorn.add_command(uvicorn.main, name=cli_uvicorn.name)
    # noinspection PyTypeChecker
    cli = click.CommandCollection(sources=[cli_uvicorn])
    cli(default_map=merge_default_maps([cli_uvicorn]))

from typing import Any
from typing import List
from typing import Tuple

import click

from fastapi import FastAPI

from fastapi_gql.router import graphql_apps
from fastapi_gql.router import on_shutdown

import uvicorn

# Initialize FastAPI
(auth, default) = graphql_apps

app = FastAPI()
app.on_event("shutdown")(on_shutdown)
app.include_router(auth, prefix="/graphql/auth")
app.include_router(default, prefix="/graphql")


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
@click.group("run")
@default_bind({"app": "fastapi_gql.server:app", "port": "8080"})
def cli_uvicorn():
    pass


# invoke cli_main.
if __name__ == "__main__":
    # noinspection PyTypeChecker
    cli_uvicorn.add_command(uvicorn.main, name=cli_uvicorn.name)
    cli = click.CommandCollection(sources=[cli_uvicorn])
    cli(default_map=([cli_uvicorn]))

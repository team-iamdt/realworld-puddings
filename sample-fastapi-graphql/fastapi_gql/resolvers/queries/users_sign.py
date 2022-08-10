from typing import Any

from fastapi_gql.models.type.users import UserModel
from fastapi_gql.router import BaseAppContext
import strawberry
from strawberry.types import Info


@strawberry.field
async def validate(info: Info[BaseAppContext, Any]) -> UserModel:
    pass

import dataclasses
from typing import Optional
from uuid import UUID

from edgedb import Object
from fastapi_gql.models.base import DateTime
import pendulum
from pendulum.tz.timezone import Timezone
import strawberry


# GraphQL Type of Token
@strawberry.type
@dataclasses.dataclass
class TokenInfo:
    access_token: str


# GraphQL Type of User Model
@strawberry.type
class UserModel:
    id: UUID
    email: str
    name: str
    created_at: DateTime
    updated_at: DateTime
    deleted_at: Optional[DateTime]
    deleted: bool

    # From EdgeDB Object
    @classmethod
    def from_object(cls, obj: Object, timezone: Timezone):
        return cls(
            id=UUID(str(obj.id)),
            email=obj.email,
            name=obj.name,
            created_at=pendulum.instance(obj.created_at, tz=timezone),
            updated_at=pendulum.instance(obj.updated_at, tz=timezone),
            deleted_at=(
                pendulum.instance(obj.deleted_at, tz=timezone)
                if obj.deleted_at
                else None
            ),
            deleted=obj.deleted,
        )


# Response Data
@strawberry.type
@dataclasses.dataclass
class TokenResponse:
    token: TokenInfo
    user: UserModel

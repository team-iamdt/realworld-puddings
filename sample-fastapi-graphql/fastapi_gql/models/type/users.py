import dataclasses

from edgedb import Object
from fastapi_gql.models.type.base import BaseDataModel
import pendulum
import strawberry


# GraphQL Type of Token
@strawberry.type
@dataclasses.dataclass
class TokenInfo:
    access_token: str
    refresh_token: str


# GraphQL Type of User Model
@strawberry.type
class UserModel(BaseDataModel):
    email: str
    name: str

    # From EdgeDB Object
    @classmethod
    def from_object(cls, obj: Object, timezone: str = "Asia/Seoul"):
        value = cls()
        value.id = obj.id
        value.email = obj.email
        value.name = obj.name
        value.created_at = pendulum.instance(obj.created_at, tz=timezone)
        value.updated_at = pendulum.instance(obj.updated_at, tz=timezone)
        value.deleted_at = (
            pendulum.instance(obj.deleted_at, tz=timezone)
            if obj.deleted_at
            else None
        )
        value.deleted = obj.deleted
        return value


# Response Data
@strawberry.type
@dataclasses.dataclass
class TokenResponse:
    token: TokenInfo
    user: UserModel

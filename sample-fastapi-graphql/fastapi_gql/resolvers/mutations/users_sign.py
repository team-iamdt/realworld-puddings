from typing import Any, Dict, TypeAlias

from fastapi_gql.errors.missing_dependency_error import MissingDependencyError
from fastapi_gql.models.input.users import SignInInput, UserInput
from fastapi_gql.models.type.users import TokenInfo, TokenResponse, UserModel
from fastapi_gql.router import BaseAppContext
import jwt
import pendulum
import strawberry
from strawberry.types import Info

ContextInfo: TypeAlias = Info[BaseAppContext, Any]


def _sign_in_with_user(
    user: UserModel, config: Dict[str, str | None]
) -> TokenResponse:
    secret = config.get("JWT_SECRET_KEY")
    if secret is None or len(secret.strip()) == 0:
        raise MissingDependencyError("JWT_SECRET_KEY")

    timezone = config.get("PENDULUM_TIMEZONE")
    if timezone is None or len(timezone.strip()) == 0:
        timezone = "Asia/Seoul"

    access_token = jwt.encode(
        {
            "user_id": user.id,
            "email": user.email,
            "exp": pendulum.now(tz=timezone).add(days=1),
        },
        secret,
        algorithm="HS256",
    )

    refresh_token = jwt.encode(
        {
            "user_id": user.id,
            "exp": pendulum.now(tz=timezone).add(days=7),
        },
        secret,
        algorithm="HS256",
    )

    return TokenResponse(
        token=TokenInfo(
            access_token=access_token.decode("utf-8"),
            refresh_token=refresh_token.decode("utf-8"),
        ),
        user=user,
    )


@strawberry.mutation
async def sign_up(info: ContextInfo, user_input: UserInput) -> TokenResponse:
    pass


@strawberry.mutation
async def sign_in(
    info: ContextInfo, sign_in_input: SignInInput
) -> TokenResponse:
    pass

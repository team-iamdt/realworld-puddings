from typing import Any, Dict, Tuple, TypeAlias

from argon2 import PasswordHasher
from edgedb import AsyncIOClient, Object
from fastapi_gql.contexts import BaseAppContext
from fastapi_gql.errors.already_exists_error import AlreadyExistsError
from fastapi_gql.errors.missing_dependency_error import MissingDependencyError
from fastapi_gql.errors.not_found_error import NotFoundError
from fastapi_gql.errors.password_not_match_error import PasswordNotMatchError
from fastapi_gql.models.input.users import SignInInput, UserInput
from fastapi_gql.models.type.users import TokenInfo, TokenResponse, UserModel
from fastapi_gql.utils.get_timezone import get_timezone
import jwt
import pendulum
from starlette.requests import Request
from strawberry.types import Info

__all__ = ["sign_in", "sign_up", "refresh"]


ContextInfo: TypeAlias = Info[BaseAppContext, Any]
hasher = PasswordHasher()


def _sign_in_with_user(
    user: UserModel, config: Dict[str, str | None]
) -> TokenResponse:
    secret = config.get("JWT_SECRET_KEY")
    if secret is None or len(secret.strip()) == 0:
        raise MissingDependencyError("JWT_SECRET_KEY")

    access_token = jwt.encode(
        {
            "user_id": str(user.id),
            "email": user.email,
            "exp": pendulum.now(tz=get_timezone(config)).add(days=1),
        },
        secret,
        algorithm="HS256",
    )

    return TokenResponse(
        token=TokenInfo(
            access_token=access_token,
        ),
        user=user,
    )


async def _find_by_email(
    email: str, client: AsyncIOClient, config: Dict[str, str | None]
) -> Tuple[UserModel, str]:
    user_candidate = await client.query_single(
        """
            SELECT User {
                id,
                email,
                password,
                name,
                created_at,
                updated_at,
                deleted_at,
                deleted
            }
            FILTER User.email = <str>$email AND User.deleted = FALSE;
        """,
        email=email,
    )

    if type(user_candidate) is not Object:
        raise NotFoundError(email)

    return (
        UserModel.from_object(user_candidate, timezone=get_timezone(config)),
        user_candidate.password,
    )


async def sign_up(info: ContextInfo, user_input: UserInput) -> TokenResponse:
    edgedb_client = info.context.client
    config = info.context.config

    # 1. open the fields
    email = user_input.email
    name = user_input.name
    password = hasher.hash(user_input.password)
    created_at = pendulum.now(tz=get_timezone(config))
    updated_at = created_at
    deleted = False

    # 2. insert query
    try:
        async for tx in edgedb_client.transaction():
            async with tx:
                prev_user = await tx.query_single(
                    """
                        SELECT User{
                            id,
                            email,
                            name,
                            created_at,
                            updated_at,
                            deleted_at,
                            deleted
                        }
                        FILTER User.email = <str>$email AND
                                User.deleted = FALSE;
                    """,
                    email=email,
                )

                if prev_user is not None:
                    raise AlreadyExistsError(email)

                await tx.query(
                    """
                        INSERT User {
                            email := <str>$email,
                            name := <str>$name,
                            password := <str>$password,
                            created_at := <datetime>$created_at,
                            updated_at := <datetime>$updated_at,
                            deleted := <bool>$deleted
                        };
                    """,
                    email=email,
                    name=name,
                    password=password,
                    created_at=created_at,
                    updated_at=updated_at,
                    deleted=deleted,
                )
    except AlreadyExistsError:
        pass

    (user, _) = await _find_by_email(email, edgedb_client, config)

    # 3. execute and return sign in result
    return _sign_in_with_user(user, config)


async def sign_in(
    info: ContextInfo, sign_in_input: SignInInput
) -> TokenResponse:
    edgedb_client = info.context.client
    config = info.context.config

    # 1. find user with email
    (user, password) = await _find_by_email(
        sign_in_input.email, edgedb_client, config
    )

    # 2. check password
    if not hasher.verify(password, sign_in_input.password):
        raise PasswordNotMatchError()

    # 3. return token
    return _sign_in_with_user(user, config)


async def refresh(info: ContextInfo, access_token: str) -> TokenResponse:
    edgedb_client = info.context.client
    config = info.context.config

    # 1. decode token
    secret_key = config.get("JWT_SECRET_KEY")
    if secret_key is None or len(secret_key.strip()) == 0:
        raise MissingDependencyError("JWT_SECRET_KEY")

    payload = jwt.decode(access_token, secret_key, algorithms=["HS256"])

    # 2. find user with user email
    (user, _) = await _find_by_email(payload["email"], edgedb_client, config)

    # 3. refresh token
    return _sign_in_with_user(user, config)


async def validate(info: Info[BaseAppContext, Any]) -> UserModel:
    config = info.context.config
    edgedb_client = info.context.client
    request = info.context.request
    assert type(request) is Request

    access_token = request.headers.get("Authorization")
    if access_token is None or len(access_token.strip()) == 0:
        raise MissingDependencyError("Authorization")

    secret_key = config.get("JWT_SECRET_KEY")
    if secret_key is None or len(secret_key.strip()) == 0:
        raise MissingDependencyError("JWT_SECRET_KEY")

    payload = jwt.decode(access_token, secret_key, algorithms=["HS256"])

    (user, _) = await _find_by_email(payload["email"], edgedb_client, config)
    return user

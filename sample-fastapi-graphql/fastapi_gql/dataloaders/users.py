import asyncio
from asyncio import AbstractEventLoop
from typing import List
from typing import Optional
from uuid import UUID

from edgedb import AsyncIOClient
from edgedb import Object
from fastapi_gql.models.type.users import UserModel
from strawberry.dataloader import DataLoader


def create_user_data_loader(
    client: AsyncIOClient,
    max_batch_size: Optional[int] = None,
    cache: bool = True,
    loop: AbstractEventLoop = None,
):
    async def load_one(user_id: UUID) -> UserModel | None:
        user = await client.query_single(
            """
            SELECT User FILTER User.id = <uuid>$id
        """,
            id=user_id,
        )

        if type(user) is not Object:
            return None

        return UserModel.from_object(user)

    async def load_many(user_ids: List[UUID]) -> List[UserModel | None]:
        return list(
            await asyncio.gather(*[load_one(user_id) for user_id in user_ids])
        )

    return DataLoader(
        load_many, max_batch_size=max_batch_size, cache=cache, loop=loop
    )

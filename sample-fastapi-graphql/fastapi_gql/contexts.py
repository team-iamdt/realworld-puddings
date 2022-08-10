from typing import Dict

from edgedb import AsyncIOClient
from fastapi_gql.models.type.users import UserModel
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext


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


class AppContext(BaseAppContext):
    pass

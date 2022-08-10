from pendulum import DateTime
from pydantic import UUID1


class BaseDataModel:
    id: UUID1
    created_at: DateTime
    updated_at: DateTime
    deleted_at: DateTime | None
    deleted: bool

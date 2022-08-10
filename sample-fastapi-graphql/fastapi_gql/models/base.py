from datetime import date, datetime
from typing import NewType

import pendulum
import strawberry

DateTime = strawberry.scalar(
    NewType("DateTime", pendulum.DateTime),
    serialize=lambda v: datetime.fromisoformat(v.to_iso_8601_string()),
    parse_value=lambda v: pendulum.instance(v),
)

Date = strawberry.scalar(
    NewType("Date", pendulum.Date),
    serialize=lambda v: date.fromisoformat(v.isoformat()),
    parse_value=lambda v: pendulum.instance(v),
)

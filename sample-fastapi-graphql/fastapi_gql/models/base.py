from datetime import date
from typing import NewType

import pendulum
import strawberry

DateTime = strawberry.scalar(
    NewType("DateTime", pendulum.DateTime),
    serialize=lambda v: v.to_iso8601_string(),
    parse_value=lambda v: pendulum.DateTime.fromisoformat(v),
)

Date = strawberry.scalar(
    NewType("Date", pendulum.Date),
    serialize=lambda v: v.isoformat(),
    parse_value=lambda v: pendulum.date(
        date.fromisoformat(v).year,
        date.fromisoformat(v).month,
        date.fromisoformat(v).day,
    ),
)

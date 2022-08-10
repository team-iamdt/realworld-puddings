from typing import Dict

import pendulum
from pendulum.tz.timezone import Timezone


def get_timezone(config: Dict[str, str | None] = None) -> Timezone:
    if config is None:
        config = {}

    timezone = config.get("PENDULUM_TIMEZONE")
    if timezone is None or len(timezone.strip()) == 0:
        timezone = "Asia/Seoul"

    # mypy raises "Module not callable" for pendulum timezone
    return pendulum.timezone(timezone)  # type: ignore

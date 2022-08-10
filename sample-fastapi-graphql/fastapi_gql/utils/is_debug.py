import os


def is_debug() -> bool:
    return os.environ.get("DEBUG", "false") == "true"

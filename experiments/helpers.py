from typing import Any

from experiments.constants import CHANNEL, TARGET


def is_empty(s: Any):
    if s and type(s) is str:
        s = s.strip()
    return s is None or s == "" or s == "nan" or s == "None"


def get_channel_column_name(i: int) -> str:
    """Return the name of a channel column with number i
    Needed if the rule for creating channel columns changes."""
    return f"{CHANNEL}{i}"


def get_target_column_name(i: int) -> str:
    """Return the name of a target column with number i
    Needed if the rule for creating target columns changes."""
    return f"{TARGET}{i}"


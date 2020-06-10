from typing import Any, Union

from django.contrib.contenttypes.models import ContentType

from experiments.constants import CHANNEL, TARGET

NumStr = Union[int, str]


def is_empty(s: Any):
    if s and type(s) is str:
        s = s.strip()
    return s is None or s == "" or s == "nan" or s == "None"


def get_channel_column_name(i: NumStr) -> str:
    """Return the name of a channel column with number i
    Needed if the rule for creating channel columns changes."""
    return f"{CHANNEL}{i}"


def get_target_column_name(i: NumStr) -> str:
    """Return the name of a target column with number i
    Needed if the rule for creating target columns changes."""
    return f"{TARGET}{i}"


def get_sample_attributes_column_name(column: str, i: NumStr) -> str:
    """Return the name of a samples attribute column with number i
    Needed if the rule for creating samples attributes columns changes."""
    return f"{column}_{i}"

def get_obj_id_from_name(model: str, obj_name: str) -> int:
    """Get id of object by type and name"""
    ct = ContentType.objects.get(model=model)
    instance = ct.get_object_for_this_type(name=obj_name)
    return instance.id

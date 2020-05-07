from typing import Any


def is_empty(s: Any):
    if s and type(s) is str:
        s = s.strip()
    return s is None or s == "" or s == "nan" or s == "None"
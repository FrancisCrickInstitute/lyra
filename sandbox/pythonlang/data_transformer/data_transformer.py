"""Data transformation utilities.

This module provides helpers for reshaping and normalising dictionary data.

Open feature: flatten_dict() — see TODO below.
"""

from __future__ import annotations


def normalize_keys(data: dict) -> dict:
    """Return a copy of *data* with all keys lowercased and whitespace stripped.

    Examples
    --------
    >>> normalize_keys({"  Name ": "Alice", "AGE": 30})
    {'name': 'Alice', 'age': 30}
    """
    return {str(k).strip().lower(): v for k, v in data.items()}


def flatten_dict(data: dict, separator: str = ".") -> dict:
    """Flatten a nested dictionary into a single-level dict using *separator*.

    Examples
    --------
    >>> flatten_dict({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
    {'a.b': 1, 'a.c.d': 2, 'e': 3}

    TODO: This function is not yet implemented — add your implementation here.
          Consider handling list values, None values, and deeply nested structures.
          See tests/sandbox/test_data_transformer.py for the expected behaviour.
    """
    raise NotImplementedError("flatten_dict is not yet implemented")

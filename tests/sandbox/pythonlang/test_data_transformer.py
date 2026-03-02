"""Tests for sandbox/pythonlang/data_transformer.

Scenario: flatten_dict() is a stub (raises NotImplementedError).

Goal for the agent: implement flatten_dict() in
sandbox/pythonlang/data_transformer/data_transformer.py so all tests below pass
without modifying this test file.
"""
import pytest
from sandbox.pythonlang.data_transformer import flatten_dict, normalize_keys


class TestNormalizeKeys:
    def test_lowercase(self):
        assert normalize_keys({"NAME": "Alice", "AGE": 30}) == {"name": "Alice", "age": 30}

    def test_strips_whitespace(self):
        assert normalize_keys({"  Name ": "Bob"}) == {"name": "Bob"}

    def test_empty_dict(self):
        assert normalize_keys({}) == {}

    def test_already_normalized(self):
        assert normalize_keys({"name": "Carol"}) == {"name": "Carol"}


class TestFlattenDict:
    def test_simple_nested(self):
        result = flatten_dict({"a": {"b": 1, "c": 2}})
        assert result == {"a.b": 1, "a.c": 2}

    def test_deeply_nested(self):
        result = flatten_dict({"a": {"b": {"c": {"d": 42}}}})
        assert result == {"a.b.c.d": 42}

    def test_mixed_depth(self):
        result = flatten_dict({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
        assert result == {"a.b": 1, "a.c.d": 2, "e": 3}

    def test_empty_dict(self):
        assert flatten_dict({}) == {}

    def test_flat_dict_unchanged(self):
        assert flatten_dict({"x": 1, "y": 2}) == {"x": 1, "y": 2}

    def test_custom_separator(self):
        result = flatten_dict({"a": {"b": 1}}, separator="/")
        assert result == {"a/b": 1}

    def test_none_values_preserved(self):
        result = flatten_dict({"a": {"b": None}})
        assert result == {"a.b": None}

    def test_does_not_recurse_into_lists(self):
        result = flatten_dict({"a": [1, 2, 3]})
        assert result == {"a": [1, 2, 3]}

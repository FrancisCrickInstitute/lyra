"""Tests for sandbox/pythonlang/text_processor.

Scenario: count_words() has a bug — it uses str.split(" ") instead of str.split(),
so it fails on empty strings and multi-space input.

Goal for the agent: fix count_words() so all tests below pass without
modifying the test file.
"""
import pytest
from sandbox.pythonlang.text_processor import count_words, truncate, word_frequency


class TestCountWords:
    def test_simple_sentence(self):
        assert count_words("hello world") == 2

    def test_single_word(self):
        assert count_words("hello") == 1

    def test_empty_string(self):
        # BUG: currently returns 1 because "".split(" ") == [""]
        assert count_words("") == 0

    def test_extra_spaces_between_words(self):
        # BUG: "a  b" splits to ["a", "", "b"] with split(" ") → 3 instead of 2
        assert count_words("a  b") == 2

    def test_leading_trailing_whitespace(self):
        # BUG: "  hello  " splits to ["", "", "hello", "", ""] → 5 instead of 1
        assert count_words("  hello  ") == 1

    def test_tab_separated(self):
        assert count_words("a\tb\tc") == 3

    def test_newline_separated(self):
        assert count_words("line1\nline2") == 2


class TestWordFrequency:
    def test_basic(self):
        assert word_frequency("the cat sat on the mat") == {
            "the": 2,
            "cat": 1,
            "sat": 1,
            "on": 1,
            "mat": 1,
        }

    def test_case_insensitive(self):
        assert word_frequency("The THE the") == {"the": 3}

    def test_empty_string(self):
        assert word_frequency("") == {}


class TestTruncate:
    def test_short_text_unchanged(self):
        assert truncate("hi", 10) == "hi"

    def test_exact_length_unchanged(self):
        assert truncate("hello", 5) == "hello"

    def test_truncation(self):
        assert truncate("hello world", 8) == "hello..."

    def test_custom_suffix(self):
        assert truncate("hello world", 8, suffix="…") == "hello w…"

    def test_truncation_to_zero(self):
        assert truncate("hello", 3) == "..."

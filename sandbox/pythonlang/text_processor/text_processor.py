"""Text processing utilities.

This module provides basic string manipulation helpers used across the pipeline.

Known issue: see FIXME comment in count_words().
"""


def count_words(text: str) -> int:
    """Return the number of whitespace-separated words in *text*.

    Examples
    --------
    >>> count_words("hello world")
    2
    >>> count_words("")
    0
    """
    # FIXME: str.split(" ") does not collapse consecutive spaces or strip
    # leading/trailing whitespace, so "  hello  world  " returns 5 instead of 2
    # and an empty string returns 1 instead of 0.
    return len(text.split(" "))


def word_frequency(text: str) -> dict[str, int]:
    """Return a frequency map of words in *text* (case-insensitive).

    Examples
    --------
    >>> word_frequency("The cat sat on the mat")
    {'the': 2, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1}
    """
    freq: dict[str, int] = {}
    for word in text.lower().split():
        freq[word] = freq.get(word, 0) + 1
    return freq


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Return *text* truncated to *max_length* characters, appending *suffix* if cut.

    Examples
    --------
    >>> truncate("hello world", 8)
    'hello...'
    >>> truncate("hi", 10)
    'hi'
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix

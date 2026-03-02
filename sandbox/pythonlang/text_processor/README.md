# text_processor

**Sandbox scenario: Bug Fix**

## The Bug

`count_words()` uses `str.split(" ")` (splitting on a single literal space) instead of `str.split()` (which splits on any whitespace and discards empty tokens).

This causes three classes of failure:

| Input | Expected | Actual (buggy) |
|-------|----------|----------------|
| `""` | `0` | `1` |
| `"a  b"` | `2` | `3` |
| `"  hello  "` | `1` | `5` |

## Task

Fix `count_words()` in `text_processor.py` so all tests in `tests/sandbox/pythonlang/test_text_processor.py` pass.

**Rules:**
- Do not modify any test files.
- Do not change the function signature.
- The fix should be a one-line change.

## Functions

| Function | Status | Description |
|----------|--------|-------------|
| `count_words(text)` | **Buggy** | Returns word count; fails on edge cases |
| `word_frequency(text)` | OK | Case-insensitive word frequency map |
| `truncate(text, max_length, suffix)` | OK | Truncates string with suffix |

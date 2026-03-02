# data_transformer

**Sandbox scenario: New Feature**

## The Feature

`flatten_dict()` is currently a stub that raises `NotImplementedError`. It should recursively flatten a nested dictionary into a single-level dict with dotted (or custom-separator) keys.

## Task

Implement `flatten_dict()` in `data_transformer.py` so all tests in `tests/sandbox/pythonlang/test_data_transformer.py` pass.

**Rules:**
- Do not modify any test files.
- Do not change the function signature.
- Handle: deeply nested dicts, flat dicts, empty dicts, `None` values, and list values (do not recurse into lists).

## Expected Behaviour

```python
flatten_dict({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
# → {"a.b": 1, "a.c.d": 2, "e": 3}

flatten_dict({"a": {"b": 1}}, separator="/")
# → {"a/b": 1}

flatten_dict({"a": [1, 2, 3]})
# → {"a": [1, 2, 3]}  # lists not flattened
```

## Functions

| Function | Status | Description |
|----------|--------|-------------|
| `normalize_keys(data)` | OK | Lowercases and strips whitespace from all keys |
| `flatten_dict(data, separator)` | **Not implemented** | Recursively flattens nested dict |

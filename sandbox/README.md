# Sandbox

A safe area for testing agents against realistic Python tasks before deploying them to production code.

## Structure

```
sandbox/
└── pythonlang/                 # Python sandbox modules
    ├── text_processor/         # BUG FIX scenario
    │   ├── __init__.py
    │   ├── text_processor.py   # Contains a known bug in count_words()
    │   └── README.md
    └── data_transformer/       # NEW FEATURE scenario
        ├── __init__.py
        ├── data_transformer.py # Contains a stub: flatten_dict() not implemented
        └── README.md

tests/sandbox/
└── pythonlang/
    ├── test_text_processor.py  # Tests that expose the bug (will fail until fixed)
    └── test_data_transformer.py # Tests that define the feature (will fail until implemented)
```

## Scenarios

| Module | Scenario | Task |
|--------|----------|------|
| `text_processor` | Bug fix | `count_words()` uses `str.split(" ")` — fails on empty strings and multi-space input |
| `data_transformer` | New feature | `flatten_dict()` is a stub — implement recursive dict flattening |

## Running the Sandbox Tests

Activate the virtual environment first:

```bash
source .venv/bin/activate
```

Run all sandbox tests:

```bash
pytest tests/sandbox/ -v
```

Run a specific scenario:

```bash
pytest tests/sandbox/pythonlang/test_text_processor.py -v
pytest tests/sandbox/pythonlang/test_data_transformer.py -v
```

See current failure summary without stopping:

```bash
pytest tests/sandbox/ -v --no-header
```

## Adding New Scenarios

1. Add a new language folder under `sandbox/` (e.g., `sandbox/nextflow/`) or a new module under an existing language folder.
2. Add a paired test file under `tests/sandbox/<language>/`.
3. Include a `README.md` in the module folder describing the scenario and task.

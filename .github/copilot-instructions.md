# Instructions for GitHub Copilot

This document defines coding standards and guidelines for this repository.

---

## Project Overview

**Lyra** is a Agentic primitive repository for context and prompt management.

Supported frameworks:
  - Microsoft Agentic Package Manager - https://github.com/microsoft/apm

---

## Sandbox

The `sandbox/` directory contains isolated practice scenarios for testing agents before using them on production code.

### Structure

```
sandbox/
└── pythonlang/                  # Python scenarios (other language folders may be added)
    ├── text_processor/          # Bug fix scenario
    └── data_transformer/        # New feature scenario

tests/sandbox/
└── pythonlang/
    ├── test_text_processor.py   # Paired tests for text_processor
    └── test_data_transformer.py # Paired tests for data_transformer
```

Each module folder contains a `README.md` describing the scenario, the task, rules, and expected behaviour.

### Sandbox Mode — How to Use

When working on a sandbox task:

1. Read the module `README.md` first to understand the scenario and constraints.
2. **Never modify test files** — the tests define the contract.
3. Only edit the source file in `sandbox/pythonlang/<module>/`.
4. Run tests frequently to verify progress.

### Running Sandbox Tests

```bash
# All sandbox tests
pytest tests/sandbox/ -v

# Single scenario
pytest tests/sandbox/pythonlang/test_text_processor.py -v
pytest tests/sandbox/pythonlang/test_data_transformer.py -v

# See failures without stopping
pytest tests/sandbox/ -v --no-header
```

### Adding New Scenarios

- New language: add `sandbox/<language>/` and `tests/sandbox/<language>/`
- New module: add a folder under `sandbox/pythonlang/`, a `README.md` inside it, and a paired test file under `tests/sandbox/pythonlang/`

---

## Commit Message Guidelines

All commit messages must follow these rules:

- **Single-line commits only** – No multi-line commits, no body, no footers
- Follow Conventional Commits: `type(scope): subject`
- Use scope only when it adds clarity (e.g., `feat(parser): ...`)
- Standard types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- Keep subject line to 72 characters or fewer
- Use imperative mood: "add X", not "added X" or "adds X"
- Start with lowercase (do not capitalize first word)
- No period at the end
- Describe what the change does, not what was done
- When staging contains multiple related changes, condense into one concise line

Examples:
- `feat: add user authentication middleware`
- `fix(api): handle null response in data parser`
- `docs: update installation instructions`
- `refactor: simplify database query logic`

---

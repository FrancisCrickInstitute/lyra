# Instructions for GitHub Copilot

This document defines coding standards and guidelines for this repository.

---

## Project Overview

**Lyra** is a Agentic primitive repository for context and prompt management.

Supported frameworks:
  - Microsoft Agentic Package Manager - https://github.com/microsoft/apm

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

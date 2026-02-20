# lyra

Agentic primitives repository. Provides reusable agents, instructions, prompts, and skills for AI-assisted development workflows, managed via the [Microsoft Agentic Package Manager (APM)](https://github.com/microsoft/apm).

## Contents

The `.apm/` directory contains the following primitive types:

| Type | Description |
|------|-------------|
| `agents/` | Custom GitHub Copilot agents for orchestrating development workflows |
| `instructions/` | Coding guidelines applied automatically to matching file types |
| `prompts/` | Reusable prompt templates |
| `skills/` | Reusable skill definitions |

## Setup

Requires Python 3.13+ and [`uv`](https://github.com/astral-sh/uv).

```bash
just dev
```

This creates a virtual environment, installs all dependencies, and drops you into an activated shell.

## Requirements

- Python >= 3.13
- [uv](https://github.com/astral-sh/uv)
- [just](https://github.com/casey/just)
- [apm-cli](https://github.com/microsoft/apm)

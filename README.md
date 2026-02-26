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

## Using as an APM Dependency

### Quick Install

Install a conductor agent and all its dependencies:

```bash
# For Nextflow projects
apm install FrancisCrickInstitute/lyra/agents/nextflow/conductor.agent.md

# For Python projects
apm install FrancisCrickInstitute/lyra/agents/python/python-conductor.agent.md
```


Or install a curated bundle as a single dependency path:

```bash
# Nextflow bundle (conductor + subagents/skills)
apm install FrancisCrickInstitute/lyra/packages/nextflow
apm install

# Python bundle (conductor + subagents)
apm install FrancisCrickInstitute/lyra/packages/python
apm install
```

### Project Configuration

Or declare in your project's `apm.yml`:

```yaml
name: my-project
version: 0.0.0
dependencies:
  apm:
    - FrancisCrickInstitute/lyra/agents/nextflow/conductor.agent.md
    - FrancisCrickInstitute/lyra/agents/nextflow/nextflow-subagents/code-review-subagent.agent.md
    - FrancisCrickInstitute/lyra/agents/nextflow/nextflow-subagents/planning-subagent.agent.md
```

Then run:
```bash
apm install
```

### Notes on Paths

- APM supports installing `owner/repo/path` packages (subdirectory/virtual packages).
- APM does not support wildcard folder installs (for example, "install all files under this folder" via glob).
- If you need a fixed set of primitives from this repo, prefer bundle paths like `FrancisCrickInstitute/lyra/packages/nextflow` or `FrancisCrickInstitute/lyra/packages/python`.

### Install Individual Components

You can also install specific components:

```bash
# Just a skill
apm install FrancisCrickInstitute/lyra/skills/nextflow-diagram-creation

# Specific subagent
apm install FrancisCrickInstitute/lyra/agents/nextflow/nextflow-subagents/planning-subagent.agent.md
apm install FrancisCrickInstitute/lyra/agents/python/python-subagents/python-planner-subagent.agent.md
```

### Troubleshooting: "not accessible or doesn't exist"

APM uses the GitHub API, which rate-limits unauthenticated requests to **60/hour**. If you hit this limit, installs will fail with "not accessible or doesn't exist" even though the file is public.

**Fix:** set `GITHUB_APM_PAT` using your existing `gh` CLI token:

```bash
export GITHUB_APM_PAT=$(gh auth token)
```

To make this permanent, add it to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
echo 'export GITHUB_APM_PAT=$(gh auth token)' >> ~/.zshrc
```

This raises the rate limit to 5,000 requests/hour.

## Requirements

- Python >= 3.13
- [uv](https://github.com/astral-sh/uv)
- [just](https://github.com/casey/just)
- [apm-cli](https://github.com/microsoft/apm)

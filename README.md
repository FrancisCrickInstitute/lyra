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

Install individual files directly into another project:

```bash
apm install FrancisCrickInstitute/lyra/instructions/python.instructions.md
```

Or declare in your project's `apm.yml`:

```yaml
name: my-project
version: 0.0.0
dependencies:
  apm:
  # Agents
  - FrancisCrickInstitute/lyra/agents/docs-updater-subagent.agent.md
  - FrancisCrickInstitute/lyra/agents/python-conductor.agent.md
  - FrancisCrickInstitute/lyra/agents/python-code-reviewer-subagent.agent.md
  - FrancisCrickInstitute/lyra/agents/python-test-writer-subagent.agent.md
  - FrancisCrickInstitute/lyra/agents/python-planner-subagent.agent.md
  - FrancisCrickInstitute/lyra/agents/python-formatter-subagent.agent.md
  - FrancisCrickInstitute/lyra/agents/python-code-writer-subagent.agent.md
  # Instructions
  - FrancisCrickInstitute/lyra/instructions/python.instructions.md
  # Skills
  - FrancisCrickInstitute/lyra/skills/nextflow-diagram-creation/SKILL.md
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

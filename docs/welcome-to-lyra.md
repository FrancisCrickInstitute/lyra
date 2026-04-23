# Welcome to Lyra — An Intro to AI Tooling

If you're new to working with AI agents, this guide explains the building blocks that Lyra provides and how they fit together. No prior experience needed.

---

## What is Lyra?

Lyra is a collection of reusable AI tools — **agents**, **skills**, and **instructions** — that you can drop into your project to get structured, high-quality AI assistance. Rather than typing freeform prompts and hoping for the best, Lyra gives you pre-built, battle-tested workflows for common tasks like writing Nextflow pipelines or developing Python packages.

Think of it like a toolbox: each tool has a specific job, and you combine them to get the outcome you want.

---

## The Building Blocks

### Agents

An **agent** is an AI assistant with a specific role and a defined set of capabilities. It knows what it's responsible for, what tools it can use, and — crucially — what it *shouldn't* do.

Lyra has two types of agent:

#### Conductor Agents

The conductor is the one you talk to. It takes your request, breaks it into steps, and delegates each step to the right specialist. It doesn't write code itself — it orchestrates.

**Example:** You ask the `nextflow-conductor`:
> "Add a FastQC quality-control step to the preprocessing pipeline."

The conductor will:
1. Hand off to the **planning subagent** to research the codebase and draft a plan
2. Present the plan to you for approval
3. Delegate implementation to the **implementation subagent**
4. Send the result to the **code review subagent**
5. Run end-to-end tests via the **test subagent**

You stay in the loop at the approval stage, but the busy work is handled for you.

#### Subagents

Subagents are specialists. Each one does exactly one thing well. You don't invoke them directly — the conductor calls them in the right sequence.

| Subagent | What it does |
|---|---|
| `nextflow-planning-subagent` | Researches the codebase and produces a structured implementation plan |
| `nextflow-impliment-subagent` | Writes Nextflow pipeline code |
| `nextflow-code-review-subagent` | Reviews code for correctness, style, and best practices |
| `nextflow-e2e-test-subagent` | Runs end-to-end pipeline tests |
| `nextflow-docs-updater-subagent` | Updates documentation to reflect changes |
| `python-test-writer-subagent` | Writes failing tests before any implementation (TDD) |
| `python-code-writer-subagent` | Writes Python code to make those tests pass |
| `python-code-reviewer-subagent` | Reviews Python code quality |
| `python-formatter-subagent` | Runs formatters and linters |
| `python-acceptance-subagent` | Verifies the implementation meets the original requirements |

---

### Skills

A **skill** is a document that teaches an agent *how* to do something well. It's loaded automatically when relevant, giving the agent domain knowledge it wouldn't have otherwise.

Skills are not run directly — they are consulted by agents when they're working on a task that matches the skill's domain.

**Example:** The `nextflow-pipeline-debugging` skill teaches agents how to:
- Use `.view()` to inspect channel contents mid-pipeline
- Read Nextflow trace files
- Navigate the work directory to find intermediate outputs

Without this skill, an agent might give you generic debugging advice. With it, you get Nextflow-specific techniques straight away.

**Available skills:**

| Skill | When it's used |
|---|---|
| `nextflow-pipeline-debugging` | Diagnosing failures in Nextflow pipeline runs |
| `nextflow-diagram-creation` | Generating pipeline architecture diagrams |
| `nf-core-modules-subworkflows` | Working with nf-core standard modules |
| `bioinformatic-tool-selection` | Choosing the right bioinformatics tool for a task |
| `airflow-writing-dags` | Writing Apache Airflow DAGs |
| `airflow-testing-dags` | Testing Airflow DAGs |
| `airflow-debugging-dags` | Debugging Airflow DAG failures |

---

### Instructions

**Instructions** are coding standards and guidelines that are automatically applied whenever the AI works on a matching file type. You don't need to remind the agent how to format code or which test framework to use — the instructions handle it.

**Example:** `python.instructions.md` applies to all `*.py` files and tells the agent:
- Use `uv` to manage the environment
- Write tests before implementation (TDD)
- Use PEP 8 style, double quotes, 4-space indentation
- Use Python 3.13+ type hint syntax (`str | int` not `Union[str, int]`)

Instructions run silently in the background. Once installed, they just work.

---

## How They Work Together

Here's an end-to-end example using the **Python bundle**:

```
You: "Add a function that parses FASTQ headers and returns the sample ID."

Conductor Agent
 └─► Plan Reviewer Subagent   — analyses the request, proposes design
 └─► [You approve the plan]
 └─► Test Writer Subagent     — writes failing tests for the new function
 └─► Code Writer Subagent     — writes code to pass those tests
 └─► Code Reviewer Subagent   — checks correctness and style
 └─► Formatter Subagent       — runs ruff/black
 └─► Acceptance Subagent      — confirms the original requirement is met
 └─► Docs Updater Subagent    — updates README / docstrings
```

Throughout this, `python.instructions.md` ensures every file follows the project's Python standards, without anyone needing to spell them out.

---

### Hooks

A **hook** is a script that runs automatically after the AI edits a file. It acts as an automated quality gate, catching problems immediately rather than waiting for you to notice them.

**Example:** The `python-quality-gate` hook fires after every Python file edit. It:
1. Runs `ruff check` on any changed `.py` files
2. Runs `pytest` for the project
3. Reports failures back to the AI so it can fix them in the same session — without you having to ask

The hook resolves tools in order of preference: `.venv` executables → `uv run` → system `PATH`. This means it works whether or not you have a virtual environment active.

Hooks are transparent to you. You ask the agent to do something, it does it, the hook validates the result, and the agent corrects any issues automatically.

**Available hooks:**

| Hook | What it does |
|---|---|
| `python-quality-gate` | Runs `ruff check` and `pytest` after every Python file change |

---

## Getting Started

The fastest way to use Lyra is to install a bundle for your project type.

**For Nextflow projects:**
```bash
apm install FrancisCrickInstitute/lyra/packages/nextflow
apm install
apm compile
```

**For Python projects:**
```bash
apm install FrancisCrickInstitute/lyra/packages/python
apm install
apm compile
```

Once installed, open GitHub Copilot Chat and select the conductor agent for your project (`@nextflow-conductor` or `@python-focused-conductor`) and describe what you want to build.

---

## Frequently Asked Questions

**Do I need to understand how agents work to use them?**
No. Just install the bundle and use the conductor. The internal orchestration is handled for you.

**Can I use individual components without the full bundle?**
Yes. You can install specific agents, skills, or instructions individually:
```bash
apm install FrancisCrickInstitute/lyra/skills/nextflow-pipeline-debugging
```

**What's APM?**
APM is the [Microsoft Agentic Package Manager](https://github.com/microsoft/apm) — it's how Lyra components are installed into your project, similar to `npm` or `pip` but for AI primitives.

**What if the agent makes a mistake?**
The conductor always pauses for your approval before implementation begins. You can review the plan, ask for changes, or reject it entirely. Code review and testing subagents also act as automated safety nets.

# Using the Scope Project Agent

The `scope-project-agent` takes a rough idea and turns it into a concrete, versioned plan document. It walks you through design, task breakdown, and — optionally — publishing tickets to an issue tracker.

---

## Install

Install just the scoping agent into your project:

```bash
apm install FrancisCrickInstitute/lyra/agents/scoping/scoping-project-agent.agent.md
apm install
apm compile
```

Then open GitHub Copilot Chat and invoke the agent:

```
@scope-project-agent
```

---

## What to Provide

Give the agent one of:

- **A freeform description** of what you want to build — a few sentences is enough to start.
- **A URL or reference** to an existing issue, ticket, or document. The agent will read it in full.

You can also provide supporting material (architecture docs, READMEs, API specs) and the agent will read those too. If you have none, just say so — the agent will proceed with what it has and state its assumptions.

---

## The Interaction Flow

### Phase 1 — Context gathering

The agent reads anything you've supplied and web-searches to resolve domain concepts it doesn't recognise. It will only ask you questions if:

- The core goal is genuinely ambiguous
- A key technical constraint is missing and would change the design
- Required input (e.g. a target repo or system) is not specified

Otherwise it states its assumptions and moves on.

### Phase 2a–c — Requirements and architecture

The agent analyses your input, proposes a high-level architecture, and identifies dependencies. This happens internally — you won't be asked to approve anything yet.

### Phase 2d — Design proposal *(first approval gate)*

The agent presents a structured design proposal:

```
## Design Proposal: {title}

### Overview         — what you're building and why
### Scope            — affected systems, components to create/modify
### Proposed Architecture
### Implementation Strategy
### Dependencies     — packages, APIs, services
### Key Decisions    — important choices and rationale
### Potential Risks  — trade-offs and uncertainties
```

**The agent stops here and waits for your response.** You can:

- Approve the proposal as-is: *"Looks good, proceed."*
- Request changes: *"Can we use a plugin architecture instead?"* — the agent revises and presents again.
- Ask questions: the agent will answer and update the proposal accordingly.

### Phase 2e — Task breakdown *(second approval gate)*

Once the design is approved, the agent produces a task table:

```
| # | Task | Component | Complexity | Depends on |
```

**The agent stops again.** Same options: approve, revise, or question.

### Phase 3 — Plan document saved

After both approvals, the agent writes a versioned plan to `plans/<slug>.md`. The file includes:

- Front matter with `title`, `created`, `updated`, `version`, and `status`
- The approved design proposal
- The approved task breakdown
- A **Milestones** section grouping tasks into delivery phases
- An **Open Questions** table for anything still unresolved

The agent confirms the file path and invites feedback.

### Phase 4 — Iteration

You can request changes to the plan at any time:

- *"Move task 3 to milestone 2."*
- *"Add a risk about data migration."*
- *"Mark the auth question as resolved — we'll use OAuth."*

If a change conflicts with a previously approved decision, the agent will flag it and ask you to confirm before applying it. Each iteration increments the `version` in the front matter.

### Phase 5 — Publish to an issue tracker *(optional)*

When the plan is ready, you can ask the agent to create tickets:

> "Create GitHub Issues for these tasks in FrancisCrickInstitute/my-repo."

The agent will confirm the tracker, repository, and scope before creating anything. Each ticket gets a structured body with context, task description, acceptance criteria, and a link back to the plan document.

---

## What Next? From Plan to Code

You have a plan saved in `plans/<slug>.md` and an empty repo. Here's how to move forward.

### 1. Pick your stack and install a bundle

The scoping agent is stack-agnostic — it doesn't care what you're building. Once you know your tech, install the matching Lyra bundle:

**Nextflow pipeline:**
```bash
apm install FrancisCrickInstitute/lyra/packages/nextflow
apm install
apm compile
```

**Python package:**
```bash
apm install FrancisCrickInstitute/lyra/packages/python
apm install
apm compile
```

This gives you a conductor, subagents, skills, and coding instructions for your stack — all pre-wired together.

### 2. Scaffold the project structure

Before handing tasks to the conductor, make sure the repo has a basic structure in place. For an empty repo this usually means:

- A `README.md` with the project name and one-line description
- A `main.nf` / `src/` directory / equivalent entry point
- A dependency file (`nextflow.config`, `pyproject.toml`, etc.)

You can ask the conductor to do this:
```
@nextflow-conductor Set up a minimal project scaffold based on plans/my-project.md.
```

### 3. Hand tasks to the conductor one at a time

Work through your plan task by task. Reference the plan so the conductor has full context:

```
@nextflow-conductor Implement task 1 from plans/my-project.md.
```

The conductor will plan, implement, review, test, and document — pausing for your approval before writing any code.

### 4. Keep the plan in sync

As work progresses, update the plan to reflect reality:

```
@scope-project-agent Mark task 1 as complete in plans/my-project.md
and move the data-validation open question to resolved — we'll validate on ingest.
```

### 5. Create tickets when the team is ready

When other people are joining or you want to track progress formally:

```
@scope-project-agent Create GitHub Issues for all remaining tasks
in FrancisCrickInstitute/my-repo.
```

---

## Customising or Replacing the Coding Instructions

Lyra's bundles ship with instructions files (e.g. `python.instructions.md`, `nextflow.instructions.md`) that tell Copilot how to write code for your project — style, testing approach, tooling, naming conventions, and so on. These apply automatically to matching file types.

If the defaults don't suit your project, you have three options.

### Option 1: Edit the installed instructions

After running `apm compile`, the instructions file will be present in your project (typically under `.github/instructions/` or the path APM resolves to). Open it and edit directly — it's plain markdown with a YAML front matter `applyTo` glob.

The structure is:

```markdown
---
applyTo: "**/*.py"
---

# Your project's Python standards

- Use single quotes for strings
- Prefer `pathlib` over `os.path`
- ...
```

Changes take effect immediately — Copilot reads the file on every request.

### Option 2: Write instructions from scratch

If you want to start fresh, create a new `.instructions.md` file anywhere Copilot can read it (`.github/instructions/` is the conventional location in VS Code):

```bash
mkdir -p .github/instructions
touch .github/instructions/my-project.instructions.md
```

The front matter `applyTo` field controls which files trigger the instructions. Use a glob pattern:

| Pattern | Applies to |
|---|---|
| `**/*.py` | All Python files |
| `workflows/**` | Everything under `workflows/` |
| `**` | Every file in the project |

Then write your standards as plain markdown. Common sections to include:

- **Environment setup** — how to install deps and run the project
- **Code style** — formatting rules, quote style, line length
- **Testing** — framework, file location, naming conventions
- **Project structure** — where source code, tests, and config live
- **Conventions** — naming patterns, error handling, logging approach

### Option 3: Layer on top of Lyra's instructions

You don't have to replace anything. Create a second instructions file with a matching `applyTo` glob and Copilot will apply both. Use this to add project-specific rules on top of the Lyra defaults:

```markdown
---
applyTo: "**/*.py"
---

# Project-specific overrides

- Use 88-character line length (we use black defaults, not 150)
- All public functions must have a NumPy-style docstring
- Log using `structlog`, not the standard `logging` module
```

Copilot merges all matching instructions files at inference time — no conflict resolution needed, but more specific rules in your file will naturally take precedence in practice.

---

## Tips

- **Start broad.** You don't need a fully formed idea — the agent will help sharpen it.
- **Use the approval gates.** The two stop points (design, then tasks) are your main levers. Take your time at each one.
- **Keep plans up to date.** The plan file is the canonical record. If scope changes mid-implementation, come back and update it — the agent will re-read it before applying any changes.
- **Open Questions are first-class.** If something is unresolved, add it to the table rather than making assumptions. It keeps the plan honest.

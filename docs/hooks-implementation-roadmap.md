# Hook Implementation Roadmap

**Date**: March 23, 2026  
**Amended**: May 11, 2026 — see "Externalised Tooling" section below; Phase 2 scope shrunk after bundling `awesome-copilot` skills.  
**Status**: Partially implemented  
**Priority**: Finish template-sanity prevention after template leakage cleanup

---

## Executive Summary

This repo packages Python and Nextflow as "reusable" bundles positioned for downstream consumers. Audit identified **critical template leakage**: some agent logic and instructions hardcoded specific project names (`polaris`, `sequencing-demux`) rather than using placeholders or project-generic wording, making bundles non-portable without user edits.

**Key Finding**: The most valuable hook is not a workflow-enforcement hook, but a **template-sanity checker** that prevents this leakage from recurring.

**Current State**: Python bundle references to `polaris` have been removed from reusable agents and instructions. Remaining template-generalization work is concentrated in the Nextflow bundle, plus adding an automated template-sanity hook so the issue does not reappear.

---

## Template Sanity: What & Why

### What It Is

A **template-sanity hook** is a preventive mechanism that scans reusable package files (agents, instructions) for leaked project-specific references and blocks commits that introduce them.

### Why It Matters

#### Problem It Solves

When someone (including future maintainers) edits `agents/python/python-focused-conductor.agent.md` or `instructions/python.instructions.md`, they might accidentally write:

```markdown
# Instead of generic:
Run `pytest --cov=<package_name>`

# They write specific:
Run `pytest --cov=polaris`
```

This error propagates to **every downstream consumer** who installs the bundle. They inherit hardcoded assumptions about project structure, tool locations, and paths.

#### Scope of Existing Leakage

**Python agents previously hardcoded "polaris" (now fixed):**
- `agents/python/python-focused-conductor.agent.md`: coverage checks
- `agents/python/python-subagents/python-code-writer-subagent.agent.md`: coverage criteria
- `agents/python/python-subagents/python-formatter-subagent.agent.md`: black/isort/ruff commands

**Nextflow agents hardcode "sequencing-demux":**
- `agents/nextflow/nextflow-subagents/nextflow-planning-subagent.agent.md`: Line 29 (work-type classification logic)
- `agents/nextflow/nextflow-subagents/nextflow-impliment-subagent.agent.md`: Line 22 (architecture assumptions)

**Instructions mix approaches inconsistently:**
- `instructions/python.instructions.md`: genericized, but still uses `<project_name>` placeholder examples alongside project-generic command wording
- `instructions/nextflow.instructions.md`: hardcodes "sequencing-demux" in title, description, and examples

### How Template-Sanity Works

A template-sanity hook would:

1. **Scan** agent and instruction files in `agents/*/` and `instructions/` for patterns:
   - Hardcoded project-specific references in reusable bundles
   - Hardcoded `sequencing-demux` references
   - Unresolved `<project_name>` placeholders
   - Unresolved `<package_name>` placeholders
   - Hardcoded absolute paths that look project-specific

2. **Block commits** that introduce these patterns with clear messages:
   ```
   ❌ Template sanity check failed
   
   agents/python/python-conductor.agent.md (line 45):
     ERROR: Hardcoded "polaris" found in reusable package
     Use placeholder <project_name> instead
     
   instructions/nextflow.instructions.md (lines 5-7):
     ERROR: Hardcoded "sequencing-demux" found
     Use placeholder <pipeline_name> instead
   ```

3. **Allow override** with `--no-hook` if absolutely necessary

---

## Hook Implementation Priority

### Tier 1: Prerequisites (Must Fix Before Adding Downstream Hooks)

| Hook | Purpose | Effort | Impact | Why First |
|------|---------|--------|--------|-----------|
| **template-sanity** | Prevent project-specific leakage in reusable packages | Low (150-200 LOC) | Prevents infinite propagation of bad assumptions | Failing to add this means future edits will repeat the problem |

### Tier 2: High-Priority Workflow Enforcement

| Hook | Purpose | Effort | Impact | Dependencies |
|-------|---------|--------|--------|--------------|
| **commit-message-validator** | Enforce Conventional Commits format (`type(scope): subject`) | Low (~50 LOC regex; scope reduced — see "Externalised Tooling" below) | Catches changelog-breaking commits before PR; improves feedback loop | Pairs with bundled `commit-message-storyteller` skill (authoring) — this hook is the enforcement half |
| **debug-cleanup** (Nextflow) | Warn/fail on debug patterns (`.view()`, `println`, `DEBUG` comments) in `.nf` files | Medium (250 LOC) | Makes implicit requirement deterministic; parallels Python quality-gate | template-sanity should exist first |

### Tier 3: Quality Gates (Can Run After Templates Fixed)

| Hook | Purpose | Effort | Impact | Dependencies |
|-------|---------|--------|--------|--------------|
| **nextflow-lint** | Run `nf-lint` or similar on pipeline files | Medium (100 LOC) | Parallel to Python quality-gate; enforces DSL2 patterns | Nextflow environment must support tools |
| **python-quality-gate-extended** | Add `--cov-fail-under=100` to existing hook | Low (10 LOC) | Guarantees coverage target before commit | python-quality-gate already exists |

### Tier 4: Nice-to-Have Warnings

| Hook | Purpose | Effort | Impact | Dependencies |
|-------|---------|--------|--------|--------------|
| **diagram-freshness** | Warn if Mermaid diagrams in docs haven't been updated alongside code changes | Medium (200 LOC) | Prevents diagram–code drift; low enforcement (advisory) | Requires heuristics for dependency matching |

---

## Recommended Implementation Order

```
Phase 1: Template Fix & Prevention (Week 1)
├── 1a. Remove "polaris" from Python agents (completed)
├── 1b. Remove "sequencing-demux" from Nextflow agents (2 files, 2 instances)
├── 1c. Standardize <project_name>/<pipeline_name> in instructions (Python completed; Nextflow pending)
└── 1d. Create + integrate template-sanity hook

Phase 2: Workflow Standardization (Week 2)
├── 2a. Create commit-message-validator hook
├── 2b. Create Nextflow debug-cleanup hook
└── 2c. Extend python-quality-gate with coverage enforcement

Phase 3: Downstream Quality (Week 3+)
├── 3a. Create nextflow-lint hook
└── 3b. Create diagram-freshness warning (optional)
```

---

## Anti-Patterns: What NOT to Hook

These should stay as **agent-side logic** or **human discipline**, not hooks:

| Anti-Pattern | Why It Fails as a Hook |
|--------------|------------------------|
| **Approval gates** (require explicit approval before merge) | Conflicts with developer autonomy; work better when embedded in agent orchestration (both conductors have them) |
| **Docstring/comment completeness** | False positives (comments preceded by `# TODO: document this`); too subjective |
| **Full test suite passing** | Already enforced by CI; hook would create duplicate feedback loop |
| **Code review approval** | GitHub native mechanism; redundant if hooked |
| **Auto-formatter enforcement** | High friction; should be pre-commit formatter, not blocking hook |

---

## Externalised Tooling: Don't Reinvent the Wheel

**Added**: May 11, 2026

Phase 2 of this roadmap originally proposed building commit-message and (implicitly) branch-naming helpers from scratch. Before doing that, it is worth checking what already exists on the APM marketplace — particularly under [`github/awesome-copilot`](https://github.com/github/awesome-copilot), which is GitHub-maintained and broadly adopted.

Two skills have now been bundled into every Lyra package (`airflow`, `nextflow`, `python`):

| Skill | What it does | Where in this roadmap |
|---|---|---|
| `github/awesome-copilot/skills/commit-message-storyteller` | Conventional Commits authoring — turns a diff into a `type(scope): subject` message with optional body and footer | Replaces the **authoring** half of Tier 2's `commit-message-validator` |
| `github/awesome-copilot/skills/git-flow-branch-creator` | Analyses changes and proposes a Git Flow branch name (`feature/...`, `release-X.Y.Z`, `hotfix-...`) | Covers a workflow concern not previously scoped in this roadmap (branch naming) |

### Impact on Phase 2

Adopting these skills means we **don't need to build authoring tooling**. The custom work shrinks accordingly:

- **`commit-message-validator`** is now a thin format checker (subject regex + type whitelist + length cap), not an end-to-end authoring system. Estimate drops from ~100 LOC to ~50 LOC. The storyteller skill handles the "what should I write?" question; the hook only enforces the format at the pre-commit boundary.
- **Branch naming** does not need its own hook. The `git-flow-branch-creator` skill is interactive and advisory — which is the right shape for a workflow concern that benefits from human judgement (a hook that *blocks* on branch name would be high-friction).

### Why this matters as a principle

The hook roadmap was scoped before the bundles had skill dependencies on third-party marketplaces. Now that we're shipping `awesome-copilot` skills, the cost-benefit shifts:

- **Maintained upstream**: bug fixes and convention updates come for free
- **Discoverable**: contributors using the bundles get these skills without extra wiring
- **Smaller surface area for us to own**: every line of hook code we don't write is a line we don't have to maintain

Before adding a new hook to this roadmap, check the APM marketplace for an existing skill that covers the *authoring* side. The hook then becomes a *validation* shim, not a full feature.

### House-style caveats

The two adopted skills have defaults that conflict with this repo's conventions:

- **`commit-message-storyteller`** defaults to multi-line messages, but `.github/copilot-instructions.md` mandates **single-line commits only**. The skill itself documents a "keep it short" mode that omits the body — users must invoke it that way, or repo-local wrapper instructions must override the default.
- **`git-flow-branch-creator`** assumes `master`/`develop` branches and `feature/...` prefixes. This repo uses `main`/`dev` and `feat/...`-style prefixes (Conventional Commits style, not Git Flow style).

These mismatches mean the skills are **advisors, not enforcers**. The Tier 2 validator hook is still load-bearing for enforcement of *our* conventions, even with the skills installed.

A follow-up worth tracking: either contribute upstream fixes (configurable branch names / commit format) or ship repo-local override instructions in `instructions/` that the bundled skills inherit from.

---

## Detailed Findings

### Workflow Patterns Identified

Audit of agents and instructions revealed 8 recurring patterns:

1. **Planning → Approval Gates** (Python: explicit; Nextflow: implicit)
   - Both conductors require human approval before proceeding
   - Hook opportunity: None (architectural requirement)

2. **Debug Artifact Cleanup** (Nextflow-explicit; Python-implicit)
   - Nextflow: Code-review stage explicitly checks for `.view()`, `println`, debug comments
   - Python: No explicit requirement (could be enforced via linter)
   - Hook opportunity: Nextflow debug-cleanup hook

3. **Test Coverage Requirements** (Python: 100% mandatory; Nextflow: No requirement)
   - Python test-writer and code-writer enforce 100% coverage before proceeding
   - Python quality-gate hook runs tests but doesn't verify coverage %
   - Hook opportunity: Extend python-quality-gate to include `--cov-fail-under=100`

4. **Generated Diagrams with Standards** (Nextflow-specific)
   - Skill: nextflow-diagram-creation (Mermaid-based)
   - Diagrams generated but no automated freshness check
   - Hook opportunity: Warn if diagrams not updated alongside pipeline changes

5. **Documentation as Final Stage** (Both conductors)
   - Both end with docs-updater stage
   - Hook opportunity: None (already in workflow)

6. **Commit Message Standardization** (Both repos)
   - Changelog workflow parses `type(scope): subject` for version bumping
   - No pre-commit validation; relies on human discipline
   - Hook opportunity: commit-message-validator hook (enforcement only — authoring is now covered by the bundled `commit-message-storyteller` skill; see "Externalised Tooling" below)

7. **Unsafe Tool Usage Without Enforcement** (Python has coverage; Nextflow lacks equivalent)
   - Python: pytest must run and pass before proceeding
   - Nextflow: No equivalent quality gate (only code-review advisory)
   - Hook opportunity: Nextflow-lint hook or debug-cleanup hook

8. **Tool/Skill Loading by Work Type** (Nextflow-specific)
   - Implementation subagent classifies work as: nextflow-primary-workflow, nextflow-workflow, nextflow-module, python-util, integration, config, python-testing, nextflow-testing, documentation
   - Each type loads different skills
   - Hook opportunity: None (architectural feature; template-sanity should verify work-type logic is generic)

---

## Decision Checklist

Before finishing Phase 1 (Template Fix), confirm:

- [ ] User agrees that templates should be generic (no hardcoded project names)
- [x] Python agents use project-generic wording rather than hardcoded package names
- [ ] Nextflow agents should use `<pipeline_name>` or equivalent placeholders
- [ ] Instructions should consistently note these are templates that require customization

Before implementing Phase 2 (Workflow Hooks), confirm:

- [ ] Phase 1 is complete and merged
- [ ] template-sanity hook is integrated and blocking
- [ ] Decision: Does commit-message-validator block commits or warn-only?
- [ ] Decision: Does debug-cleanup hook block or warn?

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Hooks add execution overhead | Use timeout limits (180s proven safe for python-quality-gate); batch independent checks |
| Hooks conflict with CI checks | Hooks provide faster feedback; CI is source of truth for merge-blocking |
| Work-type logic is missed by template-sanity | Hook should scan for regexes matching work-type classification logic (both cases found were pattern-matched) |
| Downstream consumers ignore hook warnings | Document that hooks are part of bundle contract; pre-deployment checklist |

---

## References

- **python-quality-gate hook** (existing): `hooks/python-quality-gate/` — runs ruff check + pytest on `.py` file changes
- **APM Package System**: https://github.com/microsoft/apm — defines hook discovery and lifecycle
- **Conventional Commits**: https://www.conventionalcommits.org/ — format for commit-message-validator
- **awesome-copilot skills**: https://github.com/github/awesome-copilot — source of `commit-message-storyteller` and `git-flow-branch-creator`, now bundled in all packages
- **Git Flow (nvie)**: https://nvie.com/posts/a-successful-git-branching-model/ — branching model `git-flow-branch-creator` follows
- **nf-lint**: https://github.com/nextflow-io/nf-lint — Nextflow code style enforcer
- **Python instructions**: `instructions/python.instructions.md` — PEP 8, type hints, tool standardization
- **Nextflow instructions**: `instructions/nextflow.instructions.md` — DSL2, nf-core patterns, work-type conventions

---

## Next Steps

1. **Review & Clarify** — Confirm template-generalization strategy with user
2. **Phase 1 Implementation** — Remove hardcoded project names from agents/instructions
3. **Template-Sanity Hook** — Implement and test on Phase 1 changes
4. **Phase 2 Rollout** — Implement commit-message-validator and debug-cleanup hooks
5. **Validation** — Run hooks on existing codebase; verify no false positives

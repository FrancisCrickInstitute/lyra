# Hook Implementation Roadmap

**Date**: March 23, 2026  
**Status**: Recommended Actions (Not yet implemented)  
**Priority**: Fix template leakage before downstream-facing hooks

---

## Executive Summary

This repo packages Python and Nextflow as "reusable" bundles positioned for downstream consumers. However, audit reveals **critical template leakage**: agent logic and instructions hardcode specific project names (`polaris`, `sequencing-demux`) rather than using placeholders, making bundles non-portable without user edits.

**Key Finding**: The most valuable hook is not a workflow-enforcement hook, but a **template-sanity checker** that prevents this leakage from recurring.

---

## Template Sanity: What & Why

### What It Is

A **template-sanity hook** is a preventive mechanism that scans reusable package files (agents, instructions) for leaked project-specific references and blocks commits that introduce them.

### Why It Matters

#### Problem It Solves

When someone (including future maintainers) edits `agents/python/python-conductor.agent.md` or `instructions/python.instructions.md`, they might accidentally write:

```markdown
# Instead of generic:
Run `pytest --cov=<package_name>`

# They write specific:
Run `pytest --cov=polaris`
```

This error propagates to **every downstream consumer** who installs the bundle. They inherit hardcoded assumptions about project structure, tool locations, and paths.

#### Scope of Existing Leakage

**Python agents hardcode "polaris":**
- `agents/python/python-conductor.agent.md`: Lines 18, 77, 94-96 (repo description, coverage checks, tool commands)
- `agents/python/python-subagents/python-code-writer-subagent.agent.md`: Lines 48, 78, 94, 104 (API paths, coverage criteria)
- `agents/python/python-subagents/python-formatter-subagent.agent.md`: Lines 22, 30, 38 (black/isort/ruff commands)

**Nextflow agents hardcode "sequencing-demux":**
- `agents/nextflow/nextflow-subagents/nextflow-planning-subagent.agent.md`: Line 29 (work-type classification logic)
- `agents/nextflow/nextflow-subagents/nextflow-impliment-subagent.agent.md`: Line 22 (architecture assumptions)

**Instructions mix approaches inconsistently:**
- `instructions/python.instructions.md`: Lines 27, 246, 328, 330-331, 333 (uses both `<project_name>` placeholder AND hardcoded paths)
- `instructions/nextflow.instructions.md`: Lines 5, 7, 27 (hardcodes "sequencing-demux" in title, description, examples)

### How Template-Sanity Works

A template-sanity hook would:

1. **Scan** agent and instruction files in `agents/*/` and `instructions/` for patterns:
   - Hardcoded `polaris` references
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
| **commit-message-validator** | Enforce Conventional Commits format (`type(scope): subject`) | Low (100 LOC regex) | Catches changelog-breaking commits before PR; improves feedback loop | None (can run immediately) |
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
├── 1a. Remove "polaris" from Python agents (3 files, 12 instances)
├── 1b. Remove "sequencing-demux" from Nextflow agents (2 files, 2 instances)
├── 1c. Standardize <project_name>/<pipeline_name> in instructions (2 files, 9 instances)
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
   - Hook opportunity: commit-message-validator hook

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

Before implementing Phase 1 (Template Fix), confirm:

- [ ] User agrees that templates should be generic (no hardcoded project names)
- [ ] Python agents should use `<project_name>` or `<package_name>` placeholders
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

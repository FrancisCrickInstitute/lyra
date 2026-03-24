---
name: airflow-writing-dags
description: Workflow and best practices for writing Apache Airflow 3 DAGs. Use when the user wants to write a new DAG, pipeline code, or asks about DAG patterns and conventions.
---

# DAG Writing Skill

This skill guides you through creating and validating Airflow DAGs using best practices.

The CLI is invoked as `airflow`. All commands below use this prefix.

---

## Workflow Overview

```
+-----------------------------------------+
| 1. DISCOVER                             |
|    Understand codebase & environment    |
+-----------------------------------------+
                 |
+-----------------------------------------+
| 2. PLAN                                 |
|    Propose structure, get approval      |
+-----------------------------------------+
                 |
+-----------------------------------------+
| 3. IMPLEMENT                            |
|    Write DAG following patterns         |
+-----------------------------------------+
                 |
+-----------------------------------------+
| 4. VALIDATE                             |
|    Check import errors, warnings        |
+-----------------------------------------+
                 |
+-----------------------------------------+
| 5. TEST (with user consent)             |
|    Trigger, monitor, check logs         |
+-----------------------------------------+
                 |
+-----------------------------------------+
| 6. ITERATE                              |
|    Fix issues, re-validate              |
+-----------------------------------------+
```

---

## Phase 1: Discover

Before writing code, understand the context.

### Explore the Codebase

Use file tools to find existing patterns:
- `Glob` for `**/dags/**/*.py` to find existing DAGs
- `Read` similar DAGs to understand conventions
- Check `requirements.txt` for available packages

### Query the Airflow Environment

Use `airflow` CLI commands to understand what's available:

#### DAGs

| Command | Description |
|---|---|
| `airflow dags list` | List all DAGs |
| `airflow dags details <dag_id>` | Get DAG details given a DAG id |
| `airflow dags list-import-errors` | List all DAGs that have import errors |
| `airflow dags list-jobs` | List the jobs |
| `airflow dags list-runs <dag_id>` | List DAG runs given a DAG id |
| `airflow dags next-execution <dag_id>` | Get the next logical datetimes of a DAG |
| `airflow dags pause <dag_id>` | Pause DAG(s) |
| `airflow dags unpause <dag_id>` | Resume paused DAG(s) |
| `airflow dags report` | Show DagBag loading report (includes warnings) |
| `airflow dags reserialize` | Reserialize DAGs by parsing the DagBag files |
| `airflow dags show <dag_id>` | Display DAG tasks with their dependencies |
| `airflow dags show-dependencies` | Display DAGs with their dependencies |
| `airflow dags state <dag_id> <run_id>` | Get the status of a dag run |
| `airflow dags test <dag_id>` | Execute one single DagRun locally |
| `airflow dags trigger <dag_id>` | Trigger a new DAG run |
| `airflow dags delete <dag_id>` | Delete all DB records related to the specified DAG |

#### Tasks

| Command | Description |
|---|---|
| `airflow tasks list <dag_id>` | List the tasks within a DAG |
| `airflow tasks state <dag_id> <task_id> <execution_date>` | Get the status of a task instance |
| `airflow tasks states-for-dag-run <dag_id> <run_id>` | Get the status of all task instances in a dag run |
| `airflow tasks test <dag_id> <task_id>` | Test a task instance locally |
| `airflow tasks clear <dag_id>` | Clear a set of task instances, as if they never ran |
| `airflow tasks failed-deps <dag_id> <task_id>` | Returns the unmet dependencies for a task instance |
| `airflow tasks render <dag_id> <task_id>` | Render a task instance's template(s) |

#### Connections

| Command | Description |
|---|---|
| `airflow connections list` | List connections |
| `airflow connections get <conn_id>` | Get a connection |
| `airflow connections add <conn_id>` | Add a connection |
| `airflow connections delete <conn_id>` | Delete a connection |
| `airflow connections test <conn_id>` | Test a connection |
| `airflow connections import <file>` | Import connections from a file |
| `airflow connections export <file>` | Export all connections |
| `airflow connections create-default-connections` | Create all default connections from providers |

#### Variables

| Command | Description |
|---|---|
| `airflow variables list` | List variables |
| `airflow variables get <key>` | Get variable |
| `airflow variables set <key> <value>` | Set variable |
| `airflow variables delete <key>` | Delete variable |
| `airflow variables import <file>` | Import variables |
| `airflow variables export <file>` | Export all variables |

#### Assets

| Command | Description |
|---|---|
| `airflow assets list` | List assets |
| `airflow assets details <asset_uri>` | Show asset details |
| `airflow assets materialize <asset_uri>` | Materialize an asset |

#### Backfills

| Command | Description |
|---|---|
| `airflow backfill create <dag_id>` | Create a backfill for a dag |

#### Providers

| Command | Description |
|---|---|
| `airflow providers list` | List installed providers |
| `airflow providers get <provider>` | Get detailed information about a provider |
| `airflow providers hooks` | List registered provider hooks |
| `airflow providers configs` | Get information about provider configuration |
| `airflow providers executors` | Get information about executors provided |
| `airflow providers auth-managers` | Get information about auth managers provided |
| `airflow providers secrets` | Get information about secrets backends provided |
| `airflow providers triggers` | List registered provider triggers |
| `airflow providers links` | List extra links registered by the providers |
| `airflow providers logging` | Get information about task logging handlers provided |
| `airflow providers notifications` | Get information about notifications provided |
| `airflow providers queues` | Get information about queues provided |
| `airflow providers widgets` | Get information about registered connection form widgets |
| `airflow providers behaviours` | Get information about registered connection types with custom behaviours |
| `airflow providers lazy-loaded` | Checks that provider configuration is lazy loaded |

#### Pools

| Command | Description |
|---|---|
| `airflow pools list` | List pools |
| `airflow pools get <pool>` | Get pool size |
| `airflow pools set <pool> <slots>` | Configure pool |
| `airflow pools delete <pool>` | Delete pool |
| `airflow pools import <file>` | Import pools |
| `airflow pools export <file>` | Export all pools |

#### Configuration

| Command | Description |
|---|---|
| `airflow config list` | List options for the configuration |
| `airflow config get-value <section> <key>` | Print the value of the configuration |
| `airflow config lint` | Lint options for configuration changes while migrating from 2.x to 3.0 |
| `airflow config update` | Update options for configuration changes while migrating from 2.x to 3.0 |

#### Database

| Command | Description |
|---|---|
| `airflow db check` | Check if the database can be reached |
| `airflow db check-migrations` | Check if migrations have finished |
| `airflow db migrate` | Migrate the metadata database to the latest version |
| `airflow db clean` | Purge old records in metastore tables |
| `airflow db shell` | Run a shell to access the database |
| `airflow db downgrade` | Downgrade the schema of the metadata database |
| `airflow db reset` | Burn down and rebuild the metadata database |
| `airflow db export-archived` | Export archived data from the archive tables |
| `airflow db drop-archived` | Drop archived tables created through the db clean command |

#### Miscellaneous

| Command | Description |
|---|---|
| `airflow version` | Show the Airflow version |
| `airflow info` | Show information about current Airflow and environment |
| `airflow plugins` | Dump information about loaded plugins |
| `airflow cheat-sheet` | Display cheat sheet |
| `airflow jobs check` | Check if job(s) are still alive |

---

## Phase 2: Plan

Based on discovery, propose:

1. **DAG structure** - Tasks, dependencies, schedule
2. **Operators to use** - Based on available providers
3. **Connections needed** - Existing or to be created
4. **Variables needed** - Existing or to be created
5. **Packages needed** - Additions to requirements.txt

**Get user approval before implementing.**

---

## Phase 3: Implement

Write the DAG following best practices (see below). Key steps:

1. Create DAG file in appropriate location
2. Save the file

---

## Phase 4: Validate

Use the `airflow` CLI as a feedback loop to validate your DAG.

### Step 1: Check Import Errors

After saving, check for parse errors (Airflow will have already parsed the file):

```bash
airflow dags list-import-errors
```

- If your file appears -> **fix and retry**
- If no errors -> **continue**

Common causes: missing imports, syntax errors, missing packages.

### Step 2: Verify DAG Exists

```bash
airflow dags details <dag_id>
```

Check: DAG exists, schedule correct, tags set, paused status.

### Step 3: Check Warnings

```bash
airflow dags report
```

Look for deprecation warnings or configuration issues.

### Step 4: Explore DAG Structure

```bash
airflow dags show <dag_id>
```

Displays tasks with their dependencies. For full metadata combine with `airflow dags details <dag_id>`.

---

## Phase 5: Test

> See the **airflow-testing-dags** skill for comprehensive testing guidance.

Once validation passes, test the DAG using the workflow in the **airflow-testing-dags** skill:

1. **Get user consent** -- Always ask before triggering
2. **Trigger** -- `airflow dags trigger <dag_id>`
3. **Monitor** -- `airflow dags state <dag_id> <run_id>` or `airflow tasks states-for-dag-run <dag_id> <run_id>`
4. **Analyze results** -- Check success/failure status
5. **Debug if needed** -- `airflow tasks states-for-dag-run <dag_id> <run_id>` and `airflow tasks state <dag_id> <task_id> <execution_date>`

### Quick Test (Minimal)

```bash
# Ask user first, then:
airflow dags trigger <dag_id>
airflow dags state <dag_id> <run_id>
```

For the full test -> debug -> fix -> retest loop, see **airflow-testing-dags**.

---

## Phase 6: Iterate

If issues found:
1. Fix the code
2. Check for import errors: `airflow dags list-import-errors`
3. Re-validate (Phase 4)
4. Re-test using the **airflow-testing-dags** skill workflow (Phase 5)

---

## CLI Quick Reference

| Phase | Command | Purpose |
|-------|---------|---------|
| Discover | `airflow dags list` | List all registered DAGs |
| Discover | `airflow connections list` | List available connections |
| Discover | `airflow variables list` | List available variables |
| Discover | `airflow providers list` | List installed providers |
| Validate | `airflow dags list-import-errors` | Check for DAG parse/import errors |
| Validate | `airflow dags details <dag_id>` | Verify DAG metadata and schedule |
| Validate | `airflow dags report` | Show DagBag report including warnings |
| Validate | `airflow dags show <dag_id>` | Display task graph and dependencies |
| Test | `airflow dags trigger <dag_id>` | Manually trigger a DAG run |
| Test | `airflow dags state <dag_id> <run_id>` | Check status of a DAG run |
| Test | `airflow tasks states-for-dag-run <dag_id> <run_id>` | Check all task statuses in a run |
| Test | `airflow tasks state <dag_id> <task_id> <execution_date>` | Check a single task status |
| Debug | `airflow tasks failed-deps <dag_id> <task_id>` | Show unmet task dependencies |
| Debug | `airflow tasks clear <dag_id>` | Clear task instances to re-run |
| Debug | `airflow dags test <dag_id>` | Execute a dry-run DagRun locally |

---

## Best Practices & Anti-Patterns

For code patterns and anti-patterns, see **[reference/airflow-3-guidance.md](reference/airflow-3-guidance.md)** and the syntax reference documentation.

**Read this reference when writing new DAGs or reviewing existing ones.** It covers what patterns are correct (Airflow 3-specific behavior) and what to avoid.

---

## Related Skills

- **airflow-testing-dags**: For testing DAGs, debugging failures, and the test -> fix -> retest loop
- **airflow-debugging-dags**: For troubleshooting failed DAGs

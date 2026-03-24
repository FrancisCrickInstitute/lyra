# Airflow 3 Best Practices

Repository-specific workflow guidance, antipatterns, and best practices for writing reliable DAGs.
Target: `apache-airflow==3.1.*`, Python `>=3.13`.

**For complete syntax reference**, see the airflow-dag.instructions.md documentation.

---

## Table of Contents

1. [Critical Rules — No top-level code](#1-critical-rules--no-top-level-code)
2. [When to use what](#2-when-to-use-what)
3. [Testing](#3-testing)
4. [Code quality and linting](#4-code-quality-and-linting)
5. [Antipatterns](#5-antipatterns)

---

## 1. Critical Rules — No top-level code

**The scheduler imports every DAG file on every heartbeat (~every 30 seconds).** Any code that runs at import time runs that often, holding up the scheduler and failing hard if external services are unavailable.

### ❌ NEVER: Variables and connections at module level

```python
# BAD — evaluated at import time on every scheduler heartbeat
from airflow.models import Variable
seq_dir = Variable.get("wic_seq_data_dir")
clarity_password = Variable.get("clarity_password")
```

### ✅ ALWAYS: Inside tasks only

```python
# GOOD — deferred until the task actually executes
@task
def get_config() -> dict:
    from airflow.models import Variable
    return {
        "seq_dir": Variable.get("wic_seq_data_dir"),
        "clarity_password": Variable.get("clarity_password"),
    }
```

### ❌ NEVER: I/O, network calls, or heavy imports at module level

```python
# BAD
import sys, os
polaris_path = os.path.abspath("../../polaris")
sys.path.append(polaris_path)
from polaris.ssh.nemo import Nemo          # network-capable lib imported globally
nemo = Nemo(host="login007.nemo.thecrick.org", ...)   # object created at parse time
```

### ✅ ALWAYS: Import and instantiate inside the task

```python
# GOOD
@task
def scan_runs(run_dir: str) -> list[str]:
    from polaris.ssh.nemo import Nemo
    from airflow.models import Variable
    key = Variable.get("SSH_SVC_WIC_FLU")
    nemo = Nemo(host="login007.nemo.thecrick.org", user="svc-wic-flu", key_string=key)
    ...
```

### ✅ OK: DAG-level constants (if truly static)

```python
# OK — pure Python constants, no I/O
DAG_OWNER = "chandra"
MAX_ACTIVE_RUNS = 1
SEQUENCER_HOST = "login007.nemo.thecrick.org"
```

---

## 2. When to use what

### Assets vs TriggerDagRunOperator

| Use assets when… | Use `TriggerDagRunOperator` when… |
|---|---|
| Pipelines are logically independent and just share data | You need to fan out one call per item (`expand_kwargs`) |
| Multiple consumers may react to the same data | You need to pass structured `conf` to the triggered DAG |
| You want the UI "data lineage" view | The triggered DAG must complete before the trigger DAG continues |

**Prefer assets** for decoupled data pipelines. Use `TriggerDagRunOperator` only when you need explicit control flow.

### Sensor mode: `reschedule` vs `poke`

| Mode | Behaviour | When to use |
|---|---|---|
| `"reschedule"` | Releases the worker slot between pokes | **Any wait > ~1 minute** (I/O, file arrival) |
| `"poke"` | Holds the worker slot continuously | Sub-minute polling where slot overhead matters |

**Always use `mode="reschedule"`** for sensors that wait on file systems, external APIs, or long-running processes. The default `"poke"` will exhaust your worker pool.

### Task Groups

**Use task groups when:**
- You have 5+ related tasks that form a logical phase
- You're using `.expand()` and need to collapse mapped UI groups
- Your DAG graph is hard to read without visual grouping

**Rules:**
- Name with pipeline-phase nouns: `copy_phase`, `qc_phase`, `notify_phase`
- Avoid nesting more than two levels deep
- Task groups are purely organisational — no scheduling overhead

### Branching trigger rules

When a task must run after a branch **regardless of which path was taken**, use:

```python
@task(trigger_rule="none_failed_min_one_success")
def notify(run_id: str) -> None:
    ...
```

This ensures the task runs if any upstream branch succeeded.

### XCom: return values only

**Never call `ti.xcom_push` / `ti.xcom_pull` directly in TaskFlow DAGs.** Just return values from `@task` functions and Airflow wires them automatically.

```python
@task
def scan_runs() -> list[str]:
    return ["run_001", "run_002"]   # XCom happens automatically


@task
def process(run_id: str) -> dict:
    return {"run_id": run_id, "status": "ok"}


@dag(...)
def pipeline():
    run_ids = scan_runs()
    process.expand(run_id=run_ids)   # XCom reference wired automatically
```

### Callbacks for alerting

Attach callbacks for alerting (Slack, email, PagerDuty) without coupling logic to task code:

```python
from airflow.utils.context import Context


def on_failure(context: Context) -> None:
    dag_id  = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    run_id  = context["run_id"]
    # post to Slack / Teams / send email


@dag(
    default_args={"on_failure_callback": on_failure},  # applies to all tasks
    on_failure_callback=on_failure,                    # DAG-run level failures
    ...
)
def my_dag(): ...
```

---

## 3. Testing

Every DAG file must have a corresponding test. Tests live in `tests/` mirroring `dags/`.

### Mandatory integrity test

```python
# tests/chandra/test_sequencer_copy_trigger_dag.py
from airflow.models import DagBag


def test_dag_loads():
    dagbag = DagBag(dag_folder="dags/chandra", include_examples=False)
    assert "chandra_sequencer_copy_trigger" in dagbag.dags
    assert dagbag.import_errors == {}


def test_dag_structure():
    from dags.chandra.sequencer_copy_trigger_dag import chandra_sequencer_copy_trigger
    dag = chandra_sequencer_copy_trigger()
    task_ids = {t.task_id for t in dag.tasks}
    assert "scan_runs" in task_ids
```

### Test task logic in isolation

Unwrap the `@task` decorator with `.function` to test the underlying Python callable directly:

```python
from unittest.mock import patch, MagicMock


@patch("polaris.ssh.nemo.Nemo")
@patch("airflow.models.Variable.get", return_value="/nemo/runs")
def test_scan_runs_returns_empty_when_no_runs(mock_var, mock_nemo_cls):
    mock_nemo = MagicMock()
    mock_nemo.list_directory_objects.return_value = []
    mock_nemo_cls.return_value = mock_nemo

    from dags.chandra.sequencer_copy_trigger_dag import scan_runs
    result = scan_runs.function()

    assert result == []
```

### Parse-time performance test

Catch accidental module-level I/O before it reaches production:

```python
import time
import importlib


def test_dag_parses_quickly():
    start = time.perf_counter()
    importlib.import_module("dags.chandra.sequencer_copy_trigger_dag")
    elapsed = time.perf_counter() - start
    assert elapsed < 3.0, f"DAG parse too slow ({elapsed:.2f}s) — check for module-level I/O"
```

Run the full suite with `just test`.

> For comprehensive testing guidance including mocking, integration tests, and debugging, see the airflow-testing-dags skill.

---

## 4. Code quality and linting

Run `ruff` against your DAGs before committing. The `AIR3` rule set catches Airflow 3-specific issues — deprecated arguments, removed APIs, and patterns that will break silently at runtime.

```bash
# Check all DAGs for Airflow 3 issues
ruff check dags/ --select AIR3

# Check a single team folder
ruff check dags/chandra/ --select AIR3

# Auto-fix safe violations in-place
ruff check dags/ --select AIR3 --fix
```

The `AIR3` rules include detection of:

| Rule | What it catches |
|---|---|
| `AIR301` | `schedule_interval=` — removed in Airflow 3; use `schedule=` |
| `AIR302` | `provide_context=True` — removed in Airflow 3 |
| `AIR303` | `airflow.operators.python_operator` — old import path |
| `AIR311` | `Variable.get()` / `Connection` at module level |

The full suite (`just lint`) runs `ruff check .` with the rules configured in `pyproject.toml`. Add `--select AIR3` locally for a focused Airflow-specific pass during development.

---

## 5. Antipatterns

### Banned patterns

| Pattern | Problem | Fix |
|---|---|---|
| `Variable.get()` at module level | Runs at parse time; crashes if metadata DB is down | Move inside `@task` |
| `BaseHook.get_connection()` at module level | Same parse-time problem | Move inside `@task` |
| `sys.path.append(...)` to load `polaris` | `polaris` is installed as a package — no path hacking needed | `from polaris.ssh.nemo import Nemo` directly |
| `DAG()` context manager + `PythonOperator` | Airflow 2 style; verbose; no automatic XCom | `@dag` + `@task` |
| `schedule_interval=...` | Removed in Airflow 3 | `schedule=...` |
| `provide_context=True` | Removed in Airflow 3 | `**context` kwarg is automatic |
| `datetime.datetime(...)` without timezone | Ambiguous; scheduler warnings | `pendulum.datetime(..., tz="UTC")` |
| `for` loop generating tasks at parse time | Fixed task count; cannot scale dynamically | `.expand()` / `.expand_kwargs()` |
| `xcom_push` / `xcom_pull` in TaskFlow tasks | Bypasses type-safe return-value wiring | Return values from `@task` |
| `BashOperator` for Python logic | Subprocess overhead; no type hints | `@task` or `@task.virtualenv` |
| `task_a.set_downstream(task_b)` | Verbose | `task_a >> task_b` |
| Catching and swallowing all exceptions in a task | Hides failures from Airflow's retry/alert logic | Let exceptions propagate; use `retries` and `on_failure_callback` |

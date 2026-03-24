# GitHub Copilot Instructions — Airflow 3

Apache Airflow 3 DAG definitions and best practices for the Francis Crick Institute.
These instructions guide code generation and review for Airflow projects.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Layout](#2-repository-layout)
3. [DAG Development Standards](#3-dag-development-standards)
4. [Variables and Connections](#4-variables-and-connections)
5. [Task Patterns](#5-task-patterns)
6. [Scheduling](#6-scheduling)
7. [Testing](#7-testing)
8. [Linting and Formatting](#8-linting-and-formatting)
9. [Running Things — the Justfile](#9-running-things--the-justfile)
10. [Deployment](#10-deployment)
11. [Dependencies](#11-dependencies)

---

## 1. Project Overview

- **Airflow version:** `apache-airflow==3.1.*`
- **Python:** `>=3.13`
- **Package manager:** `uv` (lockfile-based, do not use `pip install` directly)
- **Task runner:** `just` (see [§9](#9-running-things--the-justfile))
- **Deployment:** GitOps via ArgoCD + `git-sync`. Push to `staging` or `main` — no manual deploy step required.
- **Staging URL:** <https://stp-automation-airflow.staging.thecrick.org>

---

## 2. Repository Layout

```
dags/                   # DAG source files — one sub-folder per instrument/team
  wic/                  # WIC instrument DAGs
  sagitta/              # Sagitta instrument DAGs
tests/                  # pytest tests — mirrors dags/ structure
docs/
  deployment.md         # ArgoCD / GitOps deployment guide
  wic_dags.md           # WIC DAG reference
pyproject.toml          # Project metadata and dependencies
justfile                # Developer task runner
.github/
  instructions/
    airflow-dag.instructions.md   # Full Airflow 3 DAG syntax reference
  copilot-instructions.md         # This file
```

**DAG files live in `dags/<team>/`.** Name files `<descriptive_name>_dag.py`.

---

## 3. DAG Development Standards

See full details in the separate `airflow-dag.instructions.md` reference.

### Always use the `@dag` decorator (TaskFlow API)

```python
import pendulum
from airflow.decorators import dag, task


@dag(
    dag_id="wic_my_dag",                   # explicit, stable ID — never rely on function name alone
    schedule=None,                              # None | cron string | Asset | Timetable
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    tags=["wic"],
    doc_md=__doc__,
    default_args={
        "owner": "wic",
        "retries": 1,
        "retry_delay": pendulum.duration(minutes=5),
    },
)
def my_dag():
    ...


my_dag()   # required — registers the DAG in the DagBag
```

### Rules

| Rule | Detail |
|---|---|
| `dag_id` | Must be globally unique. Set explicitly. Prefix with the team/instrument name (e.g. `wic_`, `sagitta_`). |
| `schedule` | Use `schedule=`, not the removed `schedule_interval=`. |
| `start_date` | Belongs on `@dag` or `default_args`, **never** on individual tasks. |
| `catchup` | Always set `catchup=False` explicitly. |
| `max_active_runs=1` | Set unless you specifically need concurrent runs. |
| Module-level side effects | No I/O, DB calls, or `Variable.get()` at module import time (see [§4](#4-variables-and-connections)). |
| `doc_md` | Set to `__doc__` — write a module-level docstring describing the DAG purpose. |

### DAG ID naming convention

```
<team>_<workflow_description>_dag
# examples:
wic_sequencer_copy_trigger_dag
sagitta_clarity_flexy_sync_dag
```

---

## 4. Variables and Connections

**Never call `Variable.get()` or `BaseHook.get_connection()` at module level.** These run at parse time on every scheduler heartbeat and will fail if the metadata DB is unavailable.

```python
# BAD — module level
from airflow.models import Variable
my_var = Variable.get("my_var")   # ❌


# GOOD — inside a task
@task
def my_task() -> str:
    from airflow.models import Variable
    my_var = Variable.get("my_var", default_var="fallback")
    return my_var
```

```python
# Connection inside a task
@task
def connect() -> None:
    from airflow.hooks.base import BaseHook
    conn = BaseHook.get_connection("my_conn_id")
    # conn.host, conn.login, conn.password, conn.extra_dejson
```

---

## 5. Task Patterns

### Basic `@task`

```python
from airflow.decorators import task


@task
def extract() -> list[str]:
    return ["run_001", "run_002"]


@task(retries=3, retry_delay=pendulum.duration(seconds=30))
def process(run_id: str) -> dict:
    return {"run_id": run_id, "status": "ok"}
```

### XCom — use return values, not `xcom_push/pull`

```python
@dag(...)
def pipeline():
    items = extract()
    process(items)   # Airflow wires the XCom automatically
```

### Dynamic task mapping

```python
# Fan-out over a list
process.expand(run_id=get_run_ids())

# Fan-out with multiple args
trigger.expand_kwargs(
    get_run_ids().map(lambda rid: {"run_id": rid, "conf": {"is_lims": True}})
)

# Mix fixed and dynamic args
process.partial(timeout=300).expand(run_id=get_run_ids())
```

### Sensors

```python
from airflow.sensors.base import PokeReturnValue


@task.sensor(poke_interval=60, timeout=3600, mode="reschedule")
def wait_for_file(path: str) -> PokeReturnValue:
    from polaris.ssh.nemo import Nemo
    nemo = Nemo(...)
    done = nemo.exists(path)
    return PokeReturnValue(is_done=done, xcom_value=path if done else None)
```

Prefer `mode="reschedule"` for any wait longer than a few minutes; it releases the worker slot between pokes.

### Branching

```python
@task.branch
def route(run_type: str) -> str:
    return "process_illumina" if run_type == "illumina" else "process_other"
```

### Task dependencies

```python
# Implicit (TaskFlow) — preferred
result = transform(extract())

# Explicit bitshift
extract_task >> transform_task >> load_task

# Fan-in / fan-out
[task_a, task_b] >> task_c
```

### Params (manual/API-triggered runs)

```python
from airflow.models.param import Param


@dag(
    params={
        "run_id": Param(default="", type="string", description="Sequencing run ID"),
        "is_lims": Param(default=True, type="boolean"),
    },
)
def my_dag():
    @task
    def run(**context) -> None:
        run_id: str = context["params"]["run_id"]
        conf = context["dag_run"].conf  # from TriggerDagRunOperator
```

---

## 6. Scheduling

| Pattern | Example |
|---|---|
| Manual only | `schedule=None` |
| Cron | `schedule="0 6 * * *"` (daily 06:00 UTC) |
| Asset-driven | `schedule=my_asset` |
| Multiple assets | `schedule=asset_a & asset_b` |

Asset (data-aware) scheduling — preferred for pipelines that react to data landing:

```python
from airflow.sdk import Asset

run_asset = Asset("s3://crick-data/sequencing/runs")

@dag(schedule=None)
def producer():
    @task(outlets=[run_asset])
    def copy_run() -> None: ...

@dag(schedule=run_asset)          # triggered when producer emits the asset
def consumer(): ...
```

---

## 7. Testing

Tests live in `tests/` and mirror the `dags/` structure.

### DAG integrity test (required for every DAG)

Every DAG file must have a corresponding minimum integrity test that imports and validates the DagBag:

```python
# tests/wic/test_my_dag.py
from airflow.models import DagBag


def test_dag_loads():
    dagbag = DagBag(dag_folder="dags/wic", include_examples=False)
    assert "wic_my_dag" in dagbag.dags
    assert dagbag.import_errors == {}


def test_dag_has_no_import_errors():
    dagbag = DagBag(dag_folder="dags/wic", include_examples=False)
    assert dagbag.import_errors == {}
```

### Running tests

```bash
# All tests
just test

# With live log output
just test-cli

# Directly with pytest
pytest tests/

# Single file
pytest tests/wic/test_my_dag.py -v
```

### Test configuration (`pytest.ini` / `pyproject.toml`)

- `testpaths = ["tests"]`
- Ignored directories: `.*`, `*.egg`, `.github`, `__pycache__`, `build`, `dist`, `docs`
- Available plugins: `pytest-cov`, `pytest-sugar`, `pytest-benchmark`, `assertpy`

---

## 8. Linting and Formatting

| Tool | Purpose | Config |
|---|---|---|
| `ruff` | Fast linting (replaces flake8) | `pyproject.toml` |
| `black` | Code formatting | line-length 150 |
| `isort` | Import sorting | profile `black`, line-length 150 |
| `pylint` | Static analysis | max-line-length 150 |

**Line length: 150** — applies to all tools.

```bash
# Lint
just lint                           # runs ruff

# Format (run manually or in CI)
black dags/ tests/
isort dags/ tests/
```

Import order within files: standard library → third party → airflow → polaris/internal.

---

## 9. Running Things — the Justfile

The `justfile` is the single entry point for common developer tasks. Run with `just <recipe>`.

| Recipe | Command | Description |
|---|---|---|
| `just` / `just dev` | `just dev` | Create `.venv` if absent, sync all dev dependencies, drop into shell |
| `just test` | `just test` | Run the full pytest suite |
| `just test-cli` | `just test-cli` | Run pytest with live `INFO` log output streamed to the terminal |
| `just lint` | `just lint` | Run `ruff check .` over the whole project |
| `just python-upgrade` | `just python-upgrade` | Upgrade to the latest Python 3.13.x via `asdf`, recreate venv, re-sync |

### First-time setup

```bash
# Prerequisites: asdf, uv
just dev        # creates .venv, installs all dependencies
```

### Activate the virtual environment manually

```bash
source .venv/bin/activate
```

---

## 10. Deployment

DAG changes are deployed by **pushing to a branch** — no manual step required.

| Action | How |
|---|---|
| Deploy DAG change to staging | Push to `staging` branch |
| Deploy DAG change to production | Push to `main` branch |
| Deploy Airflow image change | Push to `stp-automation-airflow` repo; CI/CD handles the rest |

The `git-sync` sidecar in the Airflow pod polls this repo every **60 seconds** and syncs new DAG files automatically.

For full details see [docs/deployment.md](../docs/deployment.md).

### Related repositories

| Repository | Purpose |
|---|---|
| [stp-automation-airflow](https://github.com/FrancisCrickInstitute/stp-automation-airflow) | Airflow Docker image (built and pushed to ACR by CI/CD) |
| [k8s-cpad-gitops-stp-automation-airflow](https://github.com/FrancisCrickInstitute/k8s-cpad-gitops-stp-automation-airflow) | Helm values + Kustomize overlays consumed by ArgoCD |
| [polaris](https://github.com/FrancisCrickInstitute/polaris) | Internal helper library used by DAG tasks |

---

## 11. Dependencies

Dependencies are declared in `pyproject.toml` and managed by `uv`.

```bash
# Add a runtime dependency
uv add <package>

# Add a dev/test-only dependency
uv add --group dev <package>

# Sync after pulling changes
uv sync --group dev
```

**Do not use `pip install`** — it bypasses the lockfile.

Key runtime dependencies:
- `apache-airflow==3.1.*`
- `polaris` — internal SSH/LIMS/storage helper library (installed from GitHub via SSH)
- `requests`, `pydantic`, `fabric`, `toml`, `xmltodict`

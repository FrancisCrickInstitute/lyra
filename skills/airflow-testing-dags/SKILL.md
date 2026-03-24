---
name: airflow-testing-dags
description: Comprehensive guide for testing Apache Airflow DAGs including unit tests, integration tests, load tests, mocking, and best practices for Airflow 3 repositories.
---

# Airflow DAG Testing Guide

## Overview

Airflow DAGs are production-level code and require comprehensive testing to ensure reliability and correctness. This guide covers the testing approaches required for DAGs.

**When to use this skill:**
- Writing or reviewing DAG tests
- Debugging DAG loading or parsing issues
- Setting up test fixtures for Variables and Connections
- Implementing self-checks and validation within DAGs
- Optimizing DAG load performance

---

## 1. DAG Loader Tests

### Purpose
Ensure your DAG file can be imported without errors — no syntax errors, missing dependencies, or import-time failures.

### Basic Loader Test

Every DAG file must have a corresponding loader test in `tests/`. This is the **minimum required test** for every DAG.

```python
# tests/<team>/test_my_dag.py
from airflow.models import DagBag


def test_dag_loads():
    """Ensure the DAG loads without errors."""
    dagbag = DagBag(dag_folder="dags/<team>", include_examples=False)
    assert "my_dag_id" in dagbag.dags
    assert dagbag.import_errors == {}
```

### Running Loader Tests

```bash
# Run all tests
just test

# Run with live output
just test-cli

# Run specific test file
pytest tests/chandra/test_my_dag.py -v

# Quick validation: run the DAG file directly
python dags/chandra/my_dag.py
```

### Performance Testing

Measure DAG loading time to identify optimization opportunities:

```bash
# Measure DAG parse time
time python dags/chandra/my_dag.py

# Example output:
# real    0m0.699s
# user    0m0.590s
# sys     0m0.108s

# Measure Python interpreter startup overhead
time python -c ''

# Example output:
# real    0m0.073s
# user    0m0.037s
# sys     0m0.039s
```

**Interpretation:** In the example above, the DAG takes ~0.70s to load, with ~0.07s of Python startup overhead. The actual parsing time is ~0.63s.

**Best practices:**
- Run multiple times to account for caching effects
- Use the same environment as the Airflow scheduler (same dependencies, env vars)
- Compare before/after results on the same machine

---

## 2. Unit Tests

Unit tests validate DAG structure, task configuration, and custom operator behavior.

### Test DAG Structure

Verify task count, dependencies, and configuration:

```python
import pytest
from airflow.models import DagBag


@pytest.fixture()
def dagbag():
    return DagBag(dag_folder="dags/chandra", include_examples=False)


def test_dag_structure(dagbag):
    """Verify DAG has expected tasks and structure."""
    dag = dagbag.get_dag(dag_id="chandra_my_dag")
    
    assert dagbag.import_errors == {}
    assert dag is not None
    assert len(dag.tasks) == 3
    assert dag.catchup is False
    assert dag.max_active_runs == 1
```

### Test Task Dependencies

Validate task dependencies for code-generated or complex DAGs:

```python
def assert_dag_dict_equal(expected, dag):
    """Assert DAG structure matches expected dependencies."""
    assert dag.task_dict.keys() == expected.keys()
    for task_id, downstream_list in expected.items():
        assert dag.has_task(task_id)
        task = dag.get_task(task_id)
        assert task.downstream_task_ids == set(downstream_list)


def test_dag_dependencies(dagbag):
    """Verify task dependency graph is correct."""
    dag = dagbag.get_dag(dag_id="chandra_my_dag")
    assert_dag_dict_equal(
        {
            "extract": ["transform"],
            "transform": ["load"],
            "load": [],
        },
        dag,
    )
```

### Test Custom Operators

Use `dag.test()` to execute a DAG and validate task results:

```python
import pendulum
from airflow.sdk import DAG, TaskInstanceState


def test_my_custom_operator():
    """Test custom operator execution and result."""
    with DAG(
        dag_id="test_custom_operator",
        schedule=None,
        start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    ) as dag:
        task = MyCustomOperator(
            task_id="test_task",
            param="test_value",
        )

    dagrun = dag.test()
    ti = dagrun.get_task_instance(task_id="test_task")
    
    assert ti.state == TaskInstanceState.SUCCESS
    
    # Validate XCom output
    result = ti.xcom_pull()
    assert result == expected_output
```

---

## 3. Self-Checks (In-DAG Validation)

Implement validation tasks within your DAG to ensure correctness at runtime.

### Example: Validate S3 Data

```python
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

task = PushToS3(
    task_id="upload_data",
    bucket="my-bucket",
    key="data/output.parquet",
)

check = S3KeySensor(
    task_id="check_data_exists",
    bucket_key="s3://my-bucket/data/output.parquet",
    poke_interval=0,
    timeout=0,
)

task >> check
```

### Example: Health Check HTTP Service

```python
from airflow.providers.http.sensors.http import HttpSensor

start_service = StartMicroservice(...)

health_check = HttpSensor(
    task_id="verify_service_up",
    endpoint="/health",
    poke_interval=10,
    timeout=300,
)

start_service >> health_check
```

---

## 4. Mocking Variables and Connections

### Why Mock?

Reading from the Airflow metadata database adds test overhead. Mock Variables and Connections using environment variables for faster test execution.

### Mock Variables

Use `AIRFLOW_VAR_{KEY}` environment variables:

```python
from unittest.mock import patch
from airflow.models import Variable


def test_with_mocked_variable():
    """Test task that uses Airflow Variables."""
    with patch.dict("os.environ", AIRFLOW_VAR_MY_KEY="test-value"):
        result = Variable.get("my_key")
        assert result == "test-value"
```

### Mock Connections

Use `AIRFLOW_CONN_{CONN_ID}` environment variables:

```python
from unittest.mock import patch
from airflow.models import Connection


def test_with_mocked_connection():
    """Test task that uses Airflow Connections."""
    conn = Connection(
        conn_type="ssh",
        login="test_user",
        host="test-host",
        password="test-password",
    )
    conn_uri = conn.get_uri()
    
    with patch.dict("os.environ", AIRFLOW_CONN_MY_CONN=conn_uri):
        retrieved = Connection.get_connection_from_secrets("my_conn")
        assert retrieved.login == "test_user"
        assert retrieved.host == "test-host"
```

---

## 5. Environment Parameterization

### Use Environment Variables for Configuration

Never hard-code environment-specific values (paths, databases, hosts). Use environment variables to parameterize DAGs.

```python
import os

# Good: parameterized with fallback
output_path = os.environ.get("MY_DAG_OUTPUT_PATH", "s3://default-bucket/path/")
database = os.environ.get("MY_DAG_DATABASE", "dev_db")

# Bad: hard-coded
output_path = "s3://prod-bucket/path/"  # ❌
```

### Staging Environment

Testing should follow a staged deployment approach:

| Environment | Purpose | Deployment |
|---|---|---|
| Local | Development and unit testing | Manual via `just test` |
| Staging | Integration and acceptance testing | Push to `staging` branch |
| Production | Live system | Push to `main` branch |

**Workflow:**
1. Develop and test locally
2. Push to `staging` branch
3. Validate on staging environment
4. Merge to `main` for production deployment

---

## 6. Testing Checklist

For every new DAG, ensure:

- [ ] DAG loader test exists in `tests/<team>/test_<dag_name>.py`
- [ ] DAG loads without import errors (`assert dagbag.import_errors == {}`)
- [ ] DAG structure test validates task count and configuration
- [ ] Custom operators have unit tests with `.test()` execution
- [ ] Variables/Connections are mocked in tests (no DB dependency)
- [ ] DAG is parameterized with environment variables (no hard-coded values)
- [ ] Self-checks are implemented for critical data/service dependencies
- [ ] Tests pass locally: `just test`

---

## 7. Running Tests

```bash
# Run all tests
just test

# Run with live CLI output
just test-cli

# Run specific test file
pytest tests/chandra/test_my_dag.py -v

# Run specific test function
pytest tests/chandra/test_my_dag.py::test_dag_loads -v

# Run with coverage
pytest --cov=dags tests/
```

---

## Related Documentation

- [airflow.instructions.md](../../instructions/airflow.instructions.md) — Repository conventions and standards
- [airflow-dag.instructions.md](../../instructions/airflow-dag.instructions.md) — Full Airflow 3 DAG syntax reference
